// ── File: .../workflows/OrderWorkflowImpl.java

package com.example.temporal.workflows;

import com.example.temporal.activities.OrderActivities;
import com.example.temporal.model.OrderInput;
import com.example.temporal.model.OrderResult;
import io.temporal.activity.ActivityOptions;
import io.temporal.common.RetryOptions;
import io.temporal.workflow.Workflow;
import org.slf4j.Logger;

import java.time.Duration;

public class OrderWorkflowImpl implements OrderWorkflow {

    // JARGON: Workflow.getLogger
    //   Use this instead of LoggerFactory — workflow
    //   logger is replay-safe.
    private static final Logger log =
        Workflow.getLogger(OrderWorkflowImpl.class);

    // ── State (tracked by Temporal automatically) ───────
    private String  status     = "STARTED";
    private boolean approved   = false;
    private boolean cancelled  = false;
    private String  cancelReason = null;

    // ── Activity Stub ───────────────────────────────────
    // JARGON: Activity Stub
    //   A proxy object. Calling methods on it schedules
    //   activities on the Temporal server — not direct
    //   method calls.
    private final OrderActivities activities =
        Workflow.newActivityStub(
            OrderActivities.class,
            ActivityOptions.newBuilder()
                .setStartToCloseTimeout(Duration.ofSeconds(30))
                .setRetryOptions(
                    RetryOptions.newBuilder()
                        .setMaximumAttempts(5)
                        .setInitialInterval(Duration.ofSeconds(1))
                        .setBackoffCoefficient(2.0)
                        .build()
                )
                .build()
        );

    // ── Workflow Entry Point ─────────────────────────────
    @Override
    public OrderResult processOrder(OrderInput input) {

        log.info("Workflow started for order: {}", input.getOrderId());

        // Step 1: Validate
        status = "VALIDATING";
        String error = activities.validateOrder(input);
        if (!error.isEmpty()) {
            status = "REJECTED";
            return new OrderResult(false, "Validation failed: " + error);
        }

        // Step 2: Wait for approval signal (up to 10 minutes)
        // JARGON: Workflow.await
        //   Pauses workflow execution until condition is true
        //   or timeout expires. Does NOT block a thread.
        status = "AWAITING_APPROVAL";
        log.info("Waiting for approval signal...");

        boolean received = Workflow.await(
            Duration.ofMinutes(10),
            () -> approved || cancelled
        );

        if (!received || cancelled) {
            status = "CANCELLED";
            String msg = cancelReason != null
                ? cancelReason : "Approval timeout or cancellation";
            return new OrderResult(false, "Order cancelled: " + msg);
        }

        // Step 3: Process payment
        status = "PROCESSING_PAYMENT";
        String txId = activities.processPayment(
            input.getOrderId(),
            input.getCustomerId(),
            input.getAmount()
        );

        // Step 4: Send confirmation
        status = "SENDING_CONFIRMATION";
        activities.sendConfirmation(
            input.getOrderId(),
            input.getCustomerId()
        );

        // Step 5: Record order
        status = "RECORDING";
        activities.recordOrder(
            input.getOrderId(),
            input.getCustomerId(),
            input.getAmount()
        );

        status = "COMPLETED";
        log.info("Workflow completed. TX: {}", txId);
        return new OrderResult(true, "Order completed. TX: " + txId);
    }

    // ── Signal Handlers ──────────────────────────────────
    @Override
    public void approveOrder() {
        log.info("Signal received: approveOrder");
        this.approved = true;
    }

    @Override
    public void cancelOrder(String reason) {
        log.info("Signal received: cancelOrder — {}", reason);
        this.cancelled    = true;
        this.cancelReason = reason;
    }

    // ── Query Handler ────────────────────────────────────
    @Override
    public String getStatus() {
        return status;
    }
}
