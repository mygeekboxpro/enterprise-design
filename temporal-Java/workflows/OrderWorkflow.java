// ── File: .../workflows/OrderWorkflow.java
//
// JARGON: @WorkflowInterface
//   Marks this as a Temporal Workflow definition.
//
// JARGON: @SignalMethod
//   External code can call this to push an event
//   INTO a running workflow.
//
// JARGON: @QueryMethod
//   External code can call this to READ state from
//   a running workflow (read-only, no side effects).

package com.example.temporal.workflows;

import com.example.temporal.model.OrderInput;
import com.example.temporal.model.OrderResult;
import io.temporal.workflow.QueryMethod;
import io.temporal.workflow.SignalMethod;
import io.temporal.workflow.WorkflowInterface;
import io.temporal.workflow.WorkflowMethod;

@WorkflowInterface
public interface OrderWorkflow {

    @WorkflowMethod
    OrderResult processOrder(OrderInput input);

    @SignalMethod
    void approveOrder();

    @SignalMethod
    void cancelOrder(String reason);

    @QueryMethod
    String getStatus();
}
