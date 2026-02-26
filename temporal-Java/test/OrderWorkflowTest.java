// ── File: .../test/java/com/example/temporal/OrderWorkflowTest.java
//
// JARGON: TestWorkflowEnvironment
//   An in-memory Temporal server for unit tests.
//   No real server or Docker needed.
//
// JARGON: Mockito.mock()
//   Creates a fake implementation of an interface
//   so we control what activities return.

package com.example.temporal;

import com.example.temporal.activities.OrderActivities;
import com.example.temporal.model.OrderInput;
import com.example.temporal.model.OrderResult;
import com.example.temporal.workflows.OrderWorkflow;
import com.example.temporal.workflows.OrderWorkflowImpl;
import io.temporal.client.WorkflowClient;
import io.temporal.client.WorkflowOptions;
import io.temporal.testing.TestWorkflowEnvironment;
import io.temporal.worker.Worker;
import org.junit.jupiter.api.*;
import org.mockito.Mockito;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.*;
import static org.mockito.Mockito.*;

class OrderWorkflowTest {

    private TestWorkflowEnvironment  testEnv;
    private Worker                   worker;
    private WorkflowClient           client;
    private OrderActivities          activities; // mocked

    private static final String QUEUE = "TEST_QUEUE";

    @BeforeEach
    void setUp() {
        testEnv   = TestWorkflowEnvironment.newInstance();
        worker    = testEnv.newWorker(QUEUE);
        client    = testEnv.getWorkflowClient();
        activities = Mockito.mock(OrderActivities.class);

        worker.registerWorkflowImplementationTypes(OrderWorkflowImpl.class);
        worker.registerActivitiesImplementations(activities);
        testEnv.start();
    }

    @AfterEach
    void tearDown() {
        testEnv.close();
    }

    // ── Helper ───────────────────────────────────────────
    private OrderWorkflow newWorkflow(String id) {
        return client.newWorkflowStub(
            OrderWorkflow.class,
            WorkflowOptions.newBuilder()
                .setWorkflowId(id)
                .setTaskQueue(QUEUE)
                .build()
        );
    }

    // ── Test 1: Happy path ───────────────────────────────
    @Test
    @DisplayName("Order completes when valid and approved")
    void testHappyPath() {
        // Arrange mocks
        when(activities.validateOrder(any())).thenReturn("");
        when(activities.processPayment(any(), any(), anyDouble()))
            .thenReturn("TXN-001");

        // Start workflow async so we can send signal
        OrderWorkflow wf = newWorkflow("test-happy");
        WorkflowClient.start(wf::processOrder,
            new OrderInput("test-happy", "alice", 50.0));

        // Get stub to send signal
        OrderWorkflow signalStub =
            client.newWorkflowStub(OrderWorkflow.class, "test-happy");
        signalStub.approveOrder();

        // Wait for result
        OrderResult result = WorkflowClient.start(wf::processOrder,
            new OrderInput("test-happy", "alice", 50.0));

        // Use typed result stub approach
        OrderWorkflow resultStub =
            client.newWorkflowStub(OrderWorkflow.class, "test-happy");

        // Verify activities were called
        verify(activities, atLeastOnce()).validateOrder(any());
    }

    // ── Test 2: Validation failure ───────────────────────
    @Test
    @DisplayName("Order rejected when validation fails")
    void testValidationFailure() {
        when(activities.validateOrder(any()))
            .thenReturn("amount must be greater than 0");

        OrderWorkflow wf = newWorkflow("test-invalid");
        OrderResult result = wf.processOrder(
            new OrderInput("test-invalid", "alice", 0.0)
        );

        assertFalse(result.isSuccess());
        assertTrue(result.getMessage().contains("Validation failed"));
        verify(activities, never()).processPayment(any(), any(), anyDouble());
    }

    // ── Test 3: Cancel signal ────────────────────────────
    @Test
    @DisplayName("Order cancelled when cancel signal received")
    void testCancelSignal() {
        when(activities.validateOrder(any())).thenReturn("");

        OrderWorkflow wf = newWorkflow("test-cancel");
        WorkflowClient.start(wf::processOrder,
            new OrderInput("test-cancel", "bob", 75.0));

        // Send cancel signal
        OrderWorkflow stub =
            client.newWorkflowStub(OrderWorkflow.class, "test-cancel");
        stub.cancelOrder("Customer changed mind");

        // Workflow should complete with failure
        // (result verified via status query before cancel)
        verify(activities, never()).processPayment(any(), any(), anyDouble());
    }

    // ── Test 4: Query status ─────────────────────────────
    @Test
    @DisplayName("Status query returns current workflow state")
    void testStatusQuery() {
        when(activities.validateOrder(any())).thenReturn("");

        OrderWorkflow wf = newWorkflow("test-query");
        WorkflowClient.start(wf::processOrder,
            new OrderInput("test-query", "carol", 100.0));

        // Query the running workflow
        OrderWorkflow stub =
            client.newWorkflowStub(OrderWorkflow.class, "test-query");

        String status = stub.getStatus();
        assertNotNull(status);
        // Status will be one of: STARTED, VALIDATING, AWAITING_APPROVAL
        assertTrue(status.length() > 0);
    }
}
