// ── File: .../temporal/Worker.java
//
// PURPOSE: Connects to Temporal server and listens on
//          ORDER_TASK_QUEUE. Run this FIRST.

package com.example.temporal;

import com.example.temporal.activities.OrderActivitiesImpl;
import com.example.temporal.workflows.OrderWorkflowImpl;
import io.temporal.client.WorkflowClient;
import io.temporal.serviceclient.WorkflowServiceStubs;
import io.temporal.worker.WorkerFactory;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class Worker {

    private static final Logger log =
        LoggerFactory.getLogger(Worker.class);

    public static final String TASK_QUEUE = "ORDER_TASK_QUEUE";

    public static void main(String[] args) {

        // 1. Connect to Temporal server (localhost:7233)
        WorkflowServiceStubs svc =
            WorkflowServiceStubs.newLocalServiceStubs();

        // 2. Create client
        WorkflowClient client = WorkflowClient.newInstance(svc);

        // 3. Create factory and worker
        WorkerFactory factory = WorkerFactory.newInstance(client);
        io.temporal.worker.Worker worker =
            factory.newWorker(TASK_QUEUE);

        // 4. Register workflow and activity implementations
        worker.registerWorkflowImplementationTypes(OrderWorkflowImpl.class);
        worker.registerActivitiesImplementations(new OrderActivitiesImpl());

        // 5. Start listening
        factory.start();
        log.info("Worker started. Listening on: {}", TASK_QUEUE);
        log.info("Open Web UI: http://localhost:8080");
    }
}
