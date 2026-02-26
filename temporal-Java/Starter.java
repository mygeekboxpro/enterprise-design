// ── File: .../temporal/Starter.java
//
// PURPOSE: Starts a new OrderWorkflow execution.
//          Run this AFTER the Worker is running.

package com.example.temporal;

import com.example.temporal.model.OrderInput;
import com.example.temporal.model.OrderResult;
import com.example.temporal.workflows.OrderWorkflow;
import io.temporal.client.WorkflowClient;
import io.temporal.client.WorkflowOptions;
import io.temporal.serviceclient.WorkflowServiceStubs;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class Starter {

    private static final Logger log =
        LoggerFactory.getLogger(Starter.class);

    public static void main(String[] args) throws InterruptedException {

        WorkflowServiceStubs svc =
            WorkflowServiceStubs.newLocalServiceStubs();
        WorkflowClient client = WorkflowClient.newInstance(svc);

        // JARGON: WorkflowOptions
        //   Configuration for this specific execution.
        //   workflowId is your stable business identifier.
        WorkflowOptions options = WorkflowOptions.newBuilder()
            .setWorkflowId("order-001")
            .setTaskQueue(Worker.TASK_QUEUE)
            .build();

        OrderWorkflow workflow =
            client.newWorkflowStub(OrderWorkflow.class, options);

        OrderInput input = new OrderInput("order-001", "alice", 99.99);

        log.info("Starting workflow for order: {}", input.getOrderId());
        log.info("Check status at: http://localhost:8080");
        log.info("Run SendSignal.java to approve or cancel.");

        // This call blocks until the workflow completes
        OrderResult result = workflow.processOrder(input);
        log.info("Workflow result: {}", result);
    }
}
