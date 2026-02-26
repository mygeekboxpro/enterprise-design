// ── File: .../activities/OrderActivitiesImpl.java
//
// JARGON: Idempotent
//   If this activity runs twice with the same input,
//   the result is the same. Required for safe retries.

package com.example.temporal.activities;

import com.example.temporal.model.OrderInput;
import io.temporal.activity.Activity;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class OrderActivitiesImpl implements OrderActivities {

    private static final Logger log =
        LoggerFactory.getLogger(OrderActivitiesImpl.class);

    // ── Activity 1: Validate ────────────────────────────
    @Override
    public String validateOrder(OrderInput input) {
        log.info("Validating order: {}", input.getOrderId());

        if (input.getOrderId() == null || input.getOrderId().isBlank()) {
            return "orderId is required";
        }
        if (input.getCustomerId() == null || input.getCustomerId().isBlank()) {
            return "customerId is required";
        }
        if (input.getAmount() <= 0) {
            return "amount must be greater than 0";
        }

        log.info("Order {} is valid", input.getOrderId());
        return ""; // empty = no error
    }

    // ── Activity 2: Process Payment ─────────────────────
    @Override
    public String processPayment(
            String orderId, String customerId, double amount) {

        log.info("Processing payment for order {} — ${}", orderId, amount);

        // Simulate occasional transient failure (for retry demo)
        // In production: call real payment gateway here
        if (Math.random() < 0.1) {
            // JARGON: ApplicationFailure
            //   Tells Temporal this failure is retryable
            throw Activity.wrap(
                new RuntimeException("Payment gateway timeout — retrying"));
        }

        String txId = "TXN-" + orderId + "-" + System.currentTimeMillis();
        log.info("Payment success. Transaction ID: {}", txId);
        return txId;
    }

    // ── Activity 3: Send Confirmation ───────────────────
    @Override
    public void sendConfirmation(String orderId, String customerId) {
        log.info("Sending confirmation for order {} to customer {}",
            orderId, customerId);
        // In production: call email/SMS service here
        log.info("Confirmation sent.");
    }

    // ── Activity 4: Record Order ─────────────────────────
    @Override
    public void recordOrder(
            String orderId, String customerId, double amount) {

        log.info("Recording order {} in database", orderId);
        // In production: INSERT into PostgreSQL here
        log.info("Order {} recorded.", orderId);
    }
}
