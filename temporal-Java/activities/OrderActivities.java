// ── File: .../activities/OrderActivities.java
//
// JARGON: @ActivityInterface
//   Marks this interface as an Activity definition.
//   Temporal scans for this annotation at registration.

package com.example.temporal.activities;

import com.example.temporal.model.OrderInput;
import io.temporal.activity.ActivityInterface;
import io.temporal.activity.ActivityMethod;

@ActivityInterface
public interface OrderActivities {

    /**
     * Validate the order input.
     * Returns error message or empty string if valid.
     */
    @ActivityMethod
    String validateOrder(OrderInput input);

    /**
     * Charge the customer's payment method.
     * Returns transaction ID.
     */
    @ActivityMethod
    String processPayment(String orderId, String customerId, double amount);

    /**
     * Send order confirmation to customer.
     */
    @ActivityMethod
    void sendConfirmation(String orderId, String customerId);

    /**
     * Persist the completed order to the database.
     */
    @ActivityMethod
    void recordOrder(String orderId, String customerId, double amount);
}
