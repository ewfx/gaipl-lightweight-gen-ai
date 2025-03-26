package com.hackathon.ipe.web.rest;

import static com.hackathon.ipe.domain.IncidentAsserts.*;
import static com.hackathon.ipe.web.rest.TestUtil.createUpdateProxyForBean;
import static org.assertj.core.api.Assertions.assertThat;
import static org.awaitility.Awaitility.await;
import static org.hamcrest.Matchers.hasItem;
import static org.mockito.Mockito.*;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.hackathon.ipe.IntegrationTest;
import com.hackathon.ipe.domain.Incident;
import com.hackathon.ipe.repository.IncidentRepository;
import com.hackathon.ipe.repository.search.IncidentSearchRepository;
import jakarta.persistence.EntityManager;
import java.time.Instant;
import java.time.temporal.ChronoUnit;
import java.util.List;
import java.util.Random;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicLong;
import org.assertj.core.util.IterableUtil;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.data.util.Streamable;
import org.springframework.http.MediaType;
import org.springframework.security.test.context.support.WithMockUser;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.transaction.annotation.Transactional;

/**
 * Integration tests for the {@link IncidentResource} REST controller.
 */
@IntegrationTest
@AutoConfigureMockMvc
@WithMockUser
class IncidentResourceIT {

    private static final String DEFAULT_INCIDENTNUM = "AAAAAAAAAA";
    private static final String UPDATED_INCIDENTNUM = "BBBBBBBBBB";

    private static final String DEFAULT_SHORT_DESCRIPTION = "AAAAAAAAAA";
    private static final String UPDATED_SHORT_DESCRIPTION = "BBBBBBBBBB";

    private static final String DEFAULT_DESCRPTION = "AAAAAAAAAA";
    private static final String UPDATED_DESCRPTION = "BBBBBBBBBB";

    private static final String DEFAULT_STATUS = "AAAAAAAAAA";
    private static final String UPDATED_STATUS = "BBBBBBBBBB";

    private static final String DEFAULT_PRIORITY = "AAAAAAAAAA";
    private static final String UPDATED_PRIORITY = "BBBBBBBBBB";

    private static final Instant DEFAULT_OPENED_AT = Instant.ofEpochMilli(0L);
    private static final Instant UPDATED_OPENED_AT = Instant.now().truncatedTo(ChronoUnit.MILLIS);

    private static final Instant DEFAULT_RESOLVED_AT = Instant.ofEpochMilli(0L);
    private static final Instant UPDATED_RESOLVED_AT = Instant.now().truncatedTo(ChronoUnit.MILLIS);

    private static final String ENTITY_API_URL = "/api/incidents";
    private static final String ENTITY_API_URL_ID = ENTITY_API_URL + "/{id}";
    private static final String ENTITY_SEARCH_API_URL = "/api/incidents/_search";

    private static Random random = new Random();
    private static AtomicLong longCount = new AtomicLong(random.nextInt() + (2 * Integer.MAX_VALUE));

    @Autowired
    private ObjectMapper om;

    @Autowired
    private IncidentRepository incidentRepository;

    @Autowired
    private IncidentSearchRepository incidentSearchRepository;

    @Autowired
    private EntityManager em;

    @Autowired
    private MockMvc restIncidentMockMvc;

    private Incident incident;

    private Incident insertedIncident;

    /**
     * Create an entity for this test.
     *
     * This is a static method, as tests for other entities might also need it,
     * if they test an entity which requires the current entity.
     */
    public static Incident createEntity() {
        return new Incident()
            .incidentnum(DEFAULT_INCIDENTNUM)
            .shortDescription(DEFAULT_SHORT_DESCRIPTION)
            .descrption(DEFAULT_DESCRPTION)
            .status(DEFAULT_STATUS)
            .priority(DEFAULT_PRIORITY)
            .openedAt(DEFAULT_OPENED_AT)
            .resolvedAt(DEFAULT_RESOLVED_AT);
    }

    /**
     * Create an updated entity for this test.
     *
     * This is a static method, as tests for other entities might also need it,
     * if they test an entity which requires the current entity.
     */
    public static Incident createUpdatedEntity() {
        return new Incident()
            .incidentnum(UPDATED_INCIDENTNUM)
            .shortDescription(UPDATED_SHORT_DESCRIPTION)
            .descrption(UPDATED_DESCRPTION)
            .status(UPDATED_STATUS)
            .priority(UPDATED_PRIORITY)
            .openedAt(UPDATED_OPENED_AT)
            .resolvedAt(UPDATED_RESOLVED_AT);
    }

    @BeforeEach
    public void initTest() {
        incident = createEntity();
    }

    @AfterEach
    public void cleanup() {
        if (insertedIncident != null) {
            incidentRepository.delete(insertedIncident);
            incidentSearchRepository.delete(insertedIncident);
            insertedIncident = null;
        }
    }

    @Test
    @Transactional
    void createIncident() throws Exception {
        long databaseSizeBeforeCreate = getRepositoryCount();
        int searchDatabaseSizeBefore = IterableUtil.sizeOf(incidentSearchRepository.findAll());
        // Create the Incident
        var returnedIncident = om.readValue(
            restIncidentMockMvc
                .perform(post(ENTITY_API_URL).contentType(MediaType.APPLICATION_JSON).content(om.writeValueAsBytes(incident)))
                .andExpect(status().isCreated())
                .andReturn()
                .getResponse()
                .getContentAsString(),
            Incident.class
        );

        // Validate the Incident in the database
        assertIncrementedRepositoryCount(databaseSizeBeforeCreate);
        assertIncidentUpdatableFieldsEquals(returnedIncident, getPersistedIncident(returnedIncident));

        await()
            .atMost(5, TimeUnit.SECONDS)
            .untilAsserted(() -> {
                int searchDatabaseSizeAfter = IterableUtil.sizeOf(incidentSearchRepository.findAll());
                assertThat(searchDatabaseSizeAfter).isEqualTo(searchDatabaseSizeBefore + 1);
            });

        insertedIncident = returnedIncident;
    }

    @Test
    @Transactional
    void createIncidentWithExistingId() throws Exception {
        // Create the Incident with an existing ID
        incident.setId(1L);

        long databaseSizeBeforeCreate = getRepositoryCount();
        int searchDatabaseSizeBefore = IterableUtil.sizeOf(incidentSearchRepository.findAll());

        // An entity with an existing ID cannot be created, so this API call must fail
        restIncidentMockMvc
            .perform(post(ENTITY_API_URL).contentType(MediaType.APPLICATION_JSON).content(om.writeValueAsBytes(incident)))
            .andExpect(status().isBadRequest());

        // Validate the Incident in the database
        assertSameRepositoryCount(databaseSizeBeforeCreate);
        int searchDatabaseSizeAfter = IterableUtil.sizeOf(incidentSearchRepository.findAll());
        assertThat(searchDatabaseSizeAfter).isEqualTo(searchDatabaseSizeBefore);
    }

    @Test
    @Transactional
    void getAllIncidents() throws Exception {
        // Initialize the database
        insertedIncident = incidentRepository.saveAndFlush(incident);

        // Get all the incidentList
        restIncidentMockMvc
            .perform(get(ENTITY_API_URL + "?sort=id,desc"))
            .andExpect(status().isOk())
            .andExpect(content().contentType(MediaType.APPLICATION_JSON_VALUE))
            .andExpect(jsonPath("$.[*].id").value(hasItem(incident.getId().intValue())))
            .andExpect(jsonPath("$.[*].incidentnum").value(hasItem(DEFAULT_INCIDENTNUM)))
            .andExpect(jsonPath("$.[*].shortDescription").value(hasItem(DEFAULT_SHORT_DESCRIPTION)))
            .andExpect(jsonPath("$.[*].descrption").value(hasItem(DEFAULT_DESCRPTION)))
            .andExpect(jsonPath("$.[*].status").value(hasItem(DEFAULT_STATUS)))
            .andExpect(jsonPath("$.[*].priority").value(hasItem(DEFAULT_PRIORITY)))
            .andExpect(jsonPath("$.[*].openedAt").value(hasItem(DEFAULT_OPENED_AT.toString())))
            .andExpect(jsonPath("$.[*].resolvedAt").value(hasItem(DEFAULT_RESOLVED_AT.toString())));
    }

    @Test
    @Transactional
    void getIncident() throws Exception {
        // Initialize the database
        insertedIncident = incidentRepository.saveAndFlush(incident);

        // Get the incident
        restIncidentMockMvc
            .perform(get(ENTITY_API_URL_ID, incident.getId()))
            .andExpect(status().isOk())
            .andExpect(content().contentType(MediaType.APPLICATION_JSON_VALUE))
            .andExpect(jsonPath("$.id").value(incident.getId().intValue()))
            .andExpect(jsonPath("$.incidentnum").value(DEFAULT_INCIDENTNUM))
            .andExpect(jsonPath("$.shortDescription").value(DEFAULT_SHORT_DESCRIPTION))
            .andExpect(jsonPath("$.descrption").value(DEFAULT_DESCRPTION))
            .andExpect(jsonPath("$.status").value(DEFAULT_STATUS))
            .andExpect(jsonPath("$.priority").value(DEFAULT_PRIORITY))
            .andExpect(jsonPath("$.openedAt").value(DEFAULT_OPENED_AT.toString()))
            .andExpect(jsonPath("$.resolvedAt").value(DEFAULT_RESOLVED_AT.toString()));
    }

    @Test
    @Transactional
    void getNonExistingIncident() throws Exception {
        // Get the incident
        restIncidentMockMvc.perform(get(ENTITY_API_URL_ID, Long.MAX_VALUE)).andExpect(status().isNotFound());
    }

    @Test
    @Transactional
    void putExistingIncident() throws Exception {
        // Initialize the database
        insertedIncident = incidentRepository.saveAndFlush(incident);

        long databaseSizeBeforeUpdate = getRepositoryCount();
        incidentSearchRepository.save(incident);
        int searchDatabaseSizeBefore = IterableUtil.sizeOf(incidentSearchRepository.findAll());

        // Update the incident
        Incident updatedIncident = incidentRepository.findById(incident.getId()).orElseThrow();
        // Disconnect from session so that the updates on updatedIncident are not directly saved in db
        em.detach(updatedIncident);
        updatedIncident
            .incidentnum(UPDATED_INCIDENTNUM)
            .shortDescription(UPDATED_SHORT_DESCRIPTION)
            .descrption(UPDATED_DESCRPTION)
            .status(UPDATED_STATUS)
            .priority(UPDATED_PRIORITY)
            .openedAt(UPDATED_OPENED_AT)
            .resolvedAt(UPDATED_RESOLVED_AT);

        restIncidentMockMvc
            .perform(
                put(ENTITY_API_URL_ID, updatedIncident.getId())
                    .contentType(MediaType.APPLICATION_JSON)
                    .content(om.writeValueAsBytes(updatedIncident))
            )
            .andExpect(status().isOk());

        // Validate the Incident in the database
        assertSameRepositoryCount(databaseSizeBeforeUpdate);
        assertPersistedIncidentToMatchAllProperties(updatedIncident);

        await()
            .atMost(5, TimeUnit.SECONDS)
            .untilAsserted(() -> {
                int searchDatabaseSizeAfter = IterableUtil.sizeOf(incidentSearchRepository.findAll());
                assertThat(searchDatabaseSizeAfter).isEqualTo(searchDatabaseSizeBefore);
                List<Incident> incidentSearchList = Streamable.of(incidentSearchRepository.findAll()).toList();
                Incident testIncidentSearch = incidentSearchList.get(searchDatabaseSizeAfter - 1);

                assertIncidentAllPropertiesEquals(testIncidentSearch, updatedIncident);
            });
    }

    @Test
    @Transactional
    void putNonExistingIncident() throws Exception {
        long databaseSizeBeforeUpdate = getRepositoryCount();
        int searchDatabaseSizeBefore = IterableUtil.sizeOf(incidentSearchRepository.findAll());
        incident.setId(longCount.incrementAndGet());

        // If the entity doesn't have an ID, it will throw BadRequestAlertException
        restIncidentMockMvc
            .perform(
                put(ENTITY_API_URL_ID, incident.getId()).contentType(MediaType.APPLICATION_JSON).content(om.writeValueAsBytes(incident))
            )
            .andExpect(status().isBadRequest());

        // Validate the Incident in the database
        assertSameRepositoryCount(databaseSizeBeforeUpdate);
        int searchDatabaseSizeAfter = IterableUtil.sizeOf(incidentSearchRepository.findAll());
        assertThat(searchDatabaseSizeAfter).isEqualTo(searchDatabaseSizeBefore);
    }

    @Test
    @Transactional
    void putWithIdMismatchIncident() throws Exception {
        long databaseSizeBeforeUpdate = getRepositoryCount();
        int searchDatabaseSizeBefore = IterableUtil.sizeOf(incidentSearchRepository.findAll());
        incident.setId(longCount.incrementAndGet());

        // If url ID doesn't match entity ID, it will throw BadRequestAlertException
        restIncidentMockMvc
            .perform(
                put(ENTITY_API_URL_ID, longCount.incrementAndGet())
                    .contentType(MediaType.APPLICATION_JSON)
                    .content(om.writeValueAsBytes(incident))
            )
            .andExpect(status().isBadRequest());

        // Validate the Incident in the database
        assertSameRepositoryCount(databaseSizeBeforeUpdate);
        int searchDatabaseSizeAfter = IterableUtil.sizeOf(incidentSearchRepository.findAll());
        assertThat(searchDatabaseSizeAfter).isEqualTo(searchDatabaseSizeBefore);
    }

    @Test
    @Transactional
    void putWithMissingIdPathParamIncident() throws Exception {
        long databaseSizeBeforeUpdate = getRepositoryCount();
        int searchDatabaseSizeBefore = IterableUtil.sizeOf(incidentSearchRepository.findAll());
        incident.setId(longCount.incrementAndGet());

        // If url ID doesn't match entity ID, it will throw BadRequestAlertException
        restIncidentMockMvc
            .perform(put(ENTITY_API_URL).contentType(MediaType.APPLICATION_JSON).content(om.writeValueAsBytes(incident)))
            .andExpect(status().isMethodNotAllowed());

        // Validate the Incident in the database
        assertSameRepositoryCount(databaseSizeBeforeUpdate);
        int searchDatabaseSizeAfter = IterableUtil.sizeOf(incidentSearchRepository.findAll());
        assertThat(searchDatabaseSizeAfter).isEqualTo(searchDatabaseSizeBefore);
    }

    @Test
    @Transactional
    void partialUpdateIncidentWithPatch() throws Exception {
        // Initialize the database
        insertedIncident = incidentRepository.saveAndFlush(incident);

        long databaseSizeBeforeUpdate = getRepositoryCount();

        // Update the incident using partial update
        Incident partialUpdatedIncident = new Incident();
        partialUpdatedIncident.setId(incident.getId());

        partialUpdatedIncident
            .descrption(UPDATED_DESCRPTION)
            .status(UPDATED_STATUS)
            .priority(UPDATED_PRIORITY)
            .resolvedAt(UPDATED_RESOLVED_AT);

        restIncidentMockMvc
            .perform(
                patch(ENTITY_API_URL_ID, partialUpdatedIncident.getId())
                    .contentType("application/merge-patch+json")
                    .content(om.writeValueAsBytes(partialUpdatedIncident))
            )
            .andExpect(status().isOk());

        // Validate the Incident in the database

        assertSameRepositoryCount(databaseSizeBeforeUpdate);
        assertIncidentUpdatableFieldsEquals(createUpdateProxyForBean(partialUpdatedIncident, incident), getPersistedIncident(incident));
    }

    @Test
    @Transactional
    void fullUpdateIncidentWithPatch() throws Exception {
        // Initialize the database
        insertedIncident = incidentRepository.saveAndFlush(incident);

        long databaseSizeBeforeUpdate = getRepositoryCount();

        // Update the incident using partial update
        Incident partialUpdatedIncident = new Incident();
        partialUpdatedIncident.setId(incident.getId());

        partialUpdatedIncident
            .incidentnum(UPDATED_INCIDENTNUM)
            .shortDescription(UPDATED_SHORT_DESCRIPTION)
            .descrption(UPDATED_DESCRPTION)
            .status(UPDATED_STATUS)
            .priority(UPDATED_PRIORITY)
            .openedAt(UPDATED_OPENED_AT)
            .resolvedAt(UPDATED_RESOLVED_AT);

        restIncidentMockMvc
            .perform(
                patch(ENTITY_API_URL_ID, partialUpdatedIncident.getId())
                    .contentType("application/merge-patch+json")
                    .content(om.writeValueAsBytes(partialUpdatedIncident))
            )
            .andExpect(status().isOk());

        // Validate the Incident in the database

        assertSameRepositoryCount(databaseSizeBeforeUpdate);
        assertIncidentUpdatableFieldsEquals(partialUpdatedIncident, getPersistedIncident(partialUpdatedIncident));
    }

    @Test
    @Transactional
    void patchNonExistingIncident() throws Exception {
        long databaseSizeBeforeUpdate = getRepositoryCount();
        int searchDatabaseSizeBefore = IterableUtil.sizeOf(incidentSearchRepository.findAll());
        incident.setId(longCount.incrementAndGet());

        // If the entity doesn't have an ID, it will throw BadRequestAlertException
        restIncidentMockMvc
            .perform(
                patch(ENTITY_API_URL_ID, incident.getId())
                    .contentType("application/merge-patch+json")
                    .content(om.writeValueAsBytes(incident))
            )
            .andExpect(status().isBadRequest());

        // Validate the Incident in the database
        assertSameRepositoryCount(databaseSizeBeforeUpdate);
        int searchDatabaseSizeAfter = IterableUtil.sizeOf(incidentSearchRepository.findAll());
        assertThat(searchDatabaseSizeAfter).isEqualTo(searchDatabaseSizeBefore);
    }

    @Test
    @Transactional
    void patchWithIdMismatchIncident() throws Exception {
        long databaseSizeBeforeUpdate = getRepositoryCount();
        int searchDatabaseSizeBefore = IterableUtil.sizeOf(incidentSearchRepository.findAll());
        incident.setId(longCount.incrementAndGet());

        // If url ID doesn't match entity ID, it will throw BadRequestAlertException
        restIncidentMockMvc
            .perform(
                patch(ENTITY_API_URL_ID, longCount.incrementAndGet())
                    .contentType("application/merge-patch+json")
                    .content(om.writeValueAsBytes(incident))
            )
            .andExpect(status().isBadRequest());

        // Validate the Incident in the database
        assertSameRepositoryCount(databaseSizeBeforeUpdate);
        int searchDatabaseSizeAfter = IterableUtil.sizeOf(incidentSearchRepository.findAll());
        assertThat(searchDatabaseSizeAfter).isEqualTo(searchDatabaseSizeBefore);
    }

    @Test
    @Transactional
    void patchWithMissingIdPathParamIncident() throws Exception {
        long databaseSizeBeforeUpdate = getRepositoryCount();
        int searchDatabaseSizeBefore = IterableUtil.sizeOf(incidentSearchRepository.findAll());
        incident.setId(longCount.incrementAndGet());

        // If url ID doesn't match entity ID, it will throw BadRequestAlertException
        restIncidentMockMvc
            .perform(patch(ENTITY_API_URL).contentType("application/merge-patch+json").content(om.writeValueAsBytes(incident)))
            .andExpect(status().isMethodNotAllowed());

        // Validate the Incident in the database
        assertSameRepositoryCount(databaseSizeBeforeUpdate);
        int searchDatabaseSizeAfter = IterableUtil.sizeOf(incidentSearchRepository.findAll());
        assertThat(searchDatabaseSizeAfter).isEqualTo(searchDatabaseSizeBefore);
    }

    @Test
    @Transactional
    void deleteIncident() throws Exception {
        // Initialize the database
        insertedIncident = incidentRepository.saveAndFlush(incident);
        incidentRepository.save(incident);
        incidentSearchRepository.save(incident);

        long databaseSizeBeforeDelete = getRepositoryCount();
        int searchDatabaseSizeBefore = IterableUtil.sizeOf(incidentSearchRepository.findAll());
        assertThat(searchDatabaseSizeBefore).isEqualTo(databaseSizeBeforeDelete);

        // Delete the incident
        restIncidentMockMvc
            .perform(delete(ENTITY_API_URL_ID, incident.getId()).accept(MediaType.APPLICATION_JSON))
            .andExpect(status().isNoContent());

        // Validate the database contains one less item
        assertDecrementedRepositoryCount(databaseSizeBeforeDelete);
        int searchDatabaseSizeAfter = IterableUtil.sizeOf(incidentSearchRepository.findAll());
        assertThat(searchDatabaseSizeAfter).isEqualTo(searchDatabaseSizeBefore - 1);
    }

    @Test
    @Transactional
    void searchIncident() throws Exception {
        // Initialize the database
        insertedIncident = incidentRepository.saveAndFlush(incident);
        incidentSearchRepository.save(incident);

        // Search the incident
        restIncidentMockMvc
            .perform(get(ENTITY_SEARCH_API_URL + "?query=id:" + incident.getId()))
            .andExpect(status().isOk())
            .andExpect(content().contentType(MediaType.APPLICATION_JSON_VALUE))
            .andExpect(jsonPath("$.[*].id").value(hasItem(incident.getId().intValue())))
            .andExpect(jsonPath("$.[*].incidentnum").value(hasItem(DEFAULT_INCIDENTNUM)))
            .andExpect(jsonPath("$.[*].shortDescription").value(hasItem(DEFAULT_SHORT_DESCRIPTION)))
            .andExpect(jsonPath("$.[*].descrption").value(hasItem(DEFAULT_DESCRPTION)))
            .andExpect(jsonPath("$.[*].status").value(hasItem(DEFAULT_STATUS)))
            .andExpect(jsonPath("$.[*].priority").value(hasItem(DEFAULT_PRIORITY)))
            .andExpect(jsonPath("$.[*].openedAt").value(hasItem(DEFAULT_OPENED_AT.toString())))
            .andExpect(jsonPath("$.[*].resolvedAt").value(hasItem(DEFAULT_RESOLVED_AT.toString())));
    }

    protected long getRepositoryCount() {
        return incidentRepository.count();
    }

    protected void assertIncrementedRepositoryCount(long countBefore) {
        assertThat(countBefore + 1).isEqualTo(getRepositoryCount());
    }

    protected void assertDecrementedRepositoryCount(long countBefore) {
        assertThat(countBefore - 1).isEqualTo(getRepositoryCount());
    }

    protected void assertSameRepositoryCount(long countBefore) {
        assertThat(countBefore).isEqualTo(getRepositoryCount());
    }

    protected Incident getPersistedIncident(Incident incident) {
        return incidentRepository.findById(incident.getId()).orElseThrow();
    }

    protected void assertPersistedIncidentToMatchAllProperties(Incident expectedIncident) {
        assertIncidentAllPropertiesEquals(expectedIncident, getPersistedIncident(expectedIncident));
    }

    protected void assertPersistedIncidentToMatchUpdatableProperties(Incident expectedIncident) {
        assertIncidentAllUpdatablePropertiesEquals(expectedIncident, getPersistedIncident(expectedIncident));
    }
}
