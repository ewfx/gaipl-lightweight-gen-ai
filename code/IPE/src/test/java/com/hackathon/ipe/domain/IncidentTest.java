package com.hackathon.ipe.domain;

import static com.hackathon.ipe.domain.IncidentTestSamples.*;
import static org.assertj.core.api.Assertions.assertThat;

import com.hackathon.ipe.web.rest.TestUtil;
import org.junit.jupiter.api.Test;

class IncidentTest {

    @Test
    void equalsVerifier() throws Exception {
        TestUtil.equalsVerifier(Incident.class);
        Incident incident1 = getIncidentSample1();
        Incident incident2 = new Incident();
        assertThat(incident1).isNotEqualTo(incident2);

        incident2.setId(incident1.getId());
        assertThat(incident1).isEqualTo(incident2);

        incident2 = getIncidentSample2();
        assertThat(incident1).isNotEqualTo(incident2);
    }
}
