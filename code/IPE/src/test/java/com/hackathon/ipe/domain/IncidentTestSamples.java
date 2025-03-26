package com.hackathon.ipe.domain;

import java.util.Random;
import java.util.UUID;
import java.util.concurrent.atomic.AtomicLong;

public class IncidentTestSamples {

    private static final Random random = new Random();
    private static final AtomicLong longCount = new AtomicLong(random.nextInt() + (2 * Integer.MAX_VALUE));

    public static Incident getIncidentSample1() {
        return new Incident()
            .id(1L)
            .incidentnum("incidentnum1")
            .shortDescription("shortDescription1")
            .descrption("descrption1")
            .status("status1")
            .priority("priority1");
    }

    public static Incident getIncidentSample2() {
        return new Incident()
            .id(2L)
            .incidentnum("incidentnum2")
            .shortDescription("shortDescription2")
            .descrption("descrption2")
            .status("status2")
            .priority("priority2");
    }

    public static Incident getIncidentRandomSampleGenerator() {
        return new Incident()
            .id(longCount.incrementAndGet())
            .incidentnum(UUID.randomUUID().toString())
            .shortDescription(UUID.randomUUID().toString())
            .descrption(UUID.randomUUID().toString())
            .status(UUID.randomUUID().toString())
            .priority(UUID.randomUUID().toString());
    }
}
