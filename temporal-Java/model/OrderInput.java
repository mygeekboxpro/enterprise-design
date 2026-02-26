// ── File: src/main/java/com/example/temporal/model/OrderInput.java

package com.example.temporal.model;

/**
 * Input passed to the OrderWorkflow when it starts.
 * Must be serializable (Temporal uses Jackson internally).
 */
public class OrderInput {

    private String orderId;
    private String customerId;
    private double amount;

    // Required by Jackson (no-arg constructor)
    public OrderInput() {}

    public OrderInput(String orderId, String customerId, double amount) {
        this.orderId    = orderId;
        this.customerId = customerId;
        this.amount     = amount;
    }

    public String getOrderId()    { return orderId; }
    public String getCustomerId() { return customerId; }
    public double getAmount()     { return amount; }

    public void setOrderId(String orderId)       { this.orderId = orderId; }
    public void setCustomerId(String customerId) { this.customerId = customerId; }
    public void setAmount(double amount)         { this.amount = amount; }
}


// ── File: src/main/java/com/example/temporal/model/OrderResult.java

package com.example.temporal.model;

/**
 * Result returned when the OrderWorkflow completes.
 */
public class OrderResult {

    private boolean success;
    private String  message;

    public OrderResult() {}

    public OrderResult(boolean success, String message) {
        this.success = success;
        this.message = message;
    }

    public boolean isSuccess()   { return success; }
    public String  getMessage()  { return message; }

    public void setSuccess(boolean success) { this.success = success; }
    public void setMessage(String message)  { this.message = message; }

    @Override
    public String toString() {
        return "OrderResult{success=" + success
             + ", message='" + message + "'}";
    }
}
