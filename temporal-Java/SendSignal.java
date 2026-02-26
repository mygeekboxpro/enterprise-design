// ── File: .../temporal/SendSignal.java
//
// PURPOSE: Sends an approve or cancel signal to a
//          running workflow. Run in a separate terminal.

package com.example.temporal;

import com.example.temporal.workflows.OrderWorkflow;
import io.temporal.client.WorkflowClient;
import io.temporal.serviceclient.WorkflowServiceStubs;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class SendSignal {

    private static final Logger log =
        LoggerFactory.getLogger(SendSignal.class);

    public static void main(String[] args) {

        // Usage: pass "approve" or "cancel" as first arg
        // Default: approve
        String action = (args.length > 0) ? args[0] : "approve";

        WorkflowServiceStubs svc =
            WorkflowServiceStubs.newLocalServiceStubs();
        WorkflowClient client = WorkflowClient.newInstance(svc);

        // Get a stub to the already-running workflow
        OrderWorkflow workflow =
            client.newWorkflowStub(OrderWorkflow.class, "order-001");

        // Query current status first
        String status = workflow.getStatus();
        log.info("Current workflow status: {}", status);

        // Send signal
        if ("cancel".equalsIgnoreCase(action)) {
            workflow.cancelOrder("Customer requested cancellation");
            log.info("Sent CANCEL signal to order-001");
        } else {
            workflow.approveOrder();
            log.info("Sent APPROVE signal to order-001");
        }
    }
}
