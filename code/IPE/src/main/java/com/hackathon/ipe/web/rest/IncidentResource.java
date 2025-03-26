package com.hackathon.ipe.web.rest;

import com.hackathon.ipe.domain.Incident;
import com.hackathon.ipe.repository.IncidentRepository;
import com.hackathon.ipe.repository.search.IncidentSearchRepository;
import com.hackathon.ipe.web.rest.errors.BadRequestAlertException;
import com.hackathon.ipe.web.rest.errors.ElasticsearchExceptionMapper;
import java.net.URI;
import java.net.URISyntaxException;
import java.util.List;
import java.util.Objects;
import java.util.Optional;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.http.HttpHeaders;
import org.springframework.http.ResponseEntity;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.servlet.support.ServletUriComponentsBuilder;
import tech.jhipster.web.util.HeaderUtil;
import tech.jhipster.web.util.PaginationUtil;
import tech.jhipster.web.util.ResponseUtil;

/**
 * REST controller for managing {@link com.hackathon.ipe.domain.Incident}.
 */
@RestController
@RequestMapping("/api/incidents")
@Transactional
public class IncidentResource {

    private static final Logger LOG = LoggerFactory.getLogger(IncidentResource.class);

    private static final String ENTITY_NAME = "incident";

    @Value("${jhipster.clientApp.name}")
    private String applicationName;

    private final IncidentRepository incidentRepository;

    private final IncidentSearchRepository incidentSearchRepository;

    public IncidentResource(IncidentRepository incidentRepository, IncidentSearchRepository incidentSearchRepository) {
        this.incidentRepository = incidentRepository;
        this.incidentSearchRepository = incidentSearchRepository;
    }

    /**
     * {@code POST  /incidents} : Create a new incident.
     *
     * @param incident the incident to create.
     * @return the {@link ResponseEntity} with status {@code 201 (Created)} and with body the new incident, or with status {@code 400 (Bad Request)} if the incident has already an ID.
     * @throws URISyntaxException if the Location URI syntax is incorrect.
     */
    @PostMapping("")
    public ResponseEntity<Incident> createIncident(@RequestBody Incident incident) throws URISyntaxException {
        LOG.debug("REST request to save Incident : {}", incident);
        if (incident.getId() != null) {
            throw new BadRequestAlertException("A new incident cannot already have an ID", ENTITY_NAME, "idexists");
        }
        incident = incidentRepository.save(incident);
        incidentSearchRepository.index(incident);
        return ResponseEntity.created(new URI("/api/incidents/" + incident.getId()))
            .headers(HeaderUtil.createEntityCreationAlert(applicationName, false, ENTITY_NAME, incident.getId().toString()))
            .body(incident);
    }

    /**
     * {@code PUT  /incidents/:id} : Updates an existing incident.
     *
     * @param id the id of the incident to save.
     * @param incident the incident to update.
     * @return the {@link ResponseEntity} with status {@code 200 (OK)} and with body the updated incident,
     * or with status {@code 400 (Bad Request)} if the incident is not valid,
     * or with status {@code 500 (Internal Server Error)} if the incident couldn't be updated.
     * @throws URISyntaxException if the Location URI syntax is incorrect.
     */
    @PutMapping("/{id}")
    public ResponseEntity<Incident> updateIncident(
        @PathVariable(value = "id", required = false) final Long id,
        @RequestBody Incident incident
    ) throws URISyntaxException {
        LOG.debug("REST request to update Incident : {}, {}", id, incident);
        if (incident.getId() == null) {
            throw new BadRequestAlertException("Invalid id", ENTITY_NAME, "idnull");
        }
        if (!Objects.equals(id, incident.getId())) {
            throw new BadRequestAlertException("Invalid ID", ENTITY_NAME, "idinvalid");
        }

        if (!incidentRepository.existsById(id)) {
            throw new BadRequestAlertException("Entity not found", ENTITY_NAME, "idnotfound");
        }

        incident = incidentRepository.save(incident);
        incidentSearchRepository.index(incident);
        return ResponseEntity.ok()
            .headers(HeaderUtil.createEntityUpdateAlert(applicationName, false, ENTITY_NAME, incident.getId().toString()))
            .body(incident);
    }

    /**
     * {@code PATCH  /incidents/:id} : Partial updates given fields of an existing incident, field will ignore if it is null
     *
     * @param id the id of the incident to save.
     * @param incident the incident to update.
     * @return the {@link ResponseEntity} with status {@code 200 (OK)} and with body the updated incident,
     * or with status {@code 400 (Bad Request)} if the incident is not valid,
     * or with status {@code 404 (Not Found)} if the incident is not found,
     * or with status {@code 500 (Internal Server Error)} if the incident couldn't be updated.
     * @throws URISyntaxException if the Location URI syntax is incorrect.
     */
    @PatchMapping(value = "/{id}", consumes = { "application/json", "application/merge-patch+json" })
    public ResponseEntity<Incident> partialUpdateIncident(
        @PathVariable(value = "id", required = false) final Long id,
        @RequestBody Incident incident
    ) throws URISyntaxException {
        LOG.debug("REST request to partial update Incident partially : {}, {}", id, incident);
        if (incident.getId() == null) {
            throw new BadRequestAlertException("Invalid id", ENTITY_NAME, "idnull");
        }
        if (!Objects.equals(id, incident.getId())) {
            throw new BadRequestAlertException("Invalid ID", ENTITY_NAME, "idinvalid");
        }

        if (!incidentRepository.existsById(id)) {
            throw new BadRequestAlertException("Entity not found", ENTITY_NAME, "idnotfound");
        }

        Optional<Incident> result = incidentRepository
            .findById(incident.getId())
            .map(existingIncident -> {
                if (incident.getIncidentnum() != null) {
                    existingIncident.setIncidentnum(incident.getIncidentnum());
                }
                if (incident.getShortDescription() != null) {
                    existingIncident.setShortDescription(incident.getShortDescription());
                }
                if (incident.getDescrption() != null) {
                    existingIncident.setDescrption(incident.getDescrption());
                }
                if (incident.getStatus() != null) {
                    existingIncident.setStatus(incident.getStatus());
                }
                if (incident.getPriority() != null) {
                    existingIncident.setPriority(incident.getPriority());
                }
                if (incident.getOpenedAt() != null) {
                    existingIncident.setOpenedAt(incident.getOpenedAt());
                }
                if (incident.getResolvedAt() != null) {
                    existingIncident.setResolvedAt(incident.getResolvedAt());
                }

                return existingIncident;
            })
            .map(incidentRepository::save)
            .map(savedIncident -> {
                incidentSearchRepository.index(savedIncident);
                return savedIncident;
            });

        return ResponseUtil.wrapOrNotFound(
            result,
            HeaderUtil.createEntityUpdateAlert(applicationName, false, ENTITY_NAME, incident.getId().toString())
        );
    }

    /**
     * {@code GET  /incidents} : get all the incidents.
     *
     * @param pageable the pagination information.
     * @return the {@link ResponseEntity} with status {@code 200 (OK)} and the list of incidents in body.
     */
    @GetMapping("")
    public ResponseEntity<List<Incident>> getAllIncidents(@org.springdoc.core.annotations.ParameterObject Pageable pageable) {
        LOG.debug("REST request to get a page of Incidents");
        Page<Incident> page = incidentRepository.findAll(pageable);
        HttpHeaders headers = PaginationUtil.generatePaginationHttpHeaders(ServletUriComponentsBuilder.fromCurrentRequest(), page);
        return ResponseEntity.ok().headers(headers).body(page.getContent());
    }

    /**
     * {@code GET  /incidents/:id} : get the "id" incident.
     *
     * @param id the id of the incident to retrieve.
     * @return the {@link ResponseEntity} with status {@code 200 (OK)} and with body the incident, or with status {@code 404 (Not Found)}.
     */
    @GetMapping("/{id}")
    public ResponseEntity<Incident> getIncident(@PathVariable("id") Long id) {
        LOG.debug("REST request to get Incident : {}", id);
        Optional<Incident> incident = incidentRepository.findById(id);
        return ResponseUtil.wrapOrNotFound(incident);
    }

    /**
     * {@code DELETE  /incidents/:id} : delete the "id" incident.
     *
     * @param id the id of the incident to delete.
     * @return the {@link ResponseEntity} with status {@code 204 (NO_CONTENT)}.
     */
    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteIncident(@PathVariable("id") Long id) {
        LOG.debug("REST request to delete Incident : {}", id);
        incidentRepository.deleteById(id);
        incidentSearchRepository.deleteFromIndexById(id);
        return ResponseEntity.noContent()
            .headers(HeaderUtil.createEntityDeletionAlert(applicationName, false, ENTITY_NAME, id.toString()))
            .build();
    }

    /**
     * {@code SEARCH  /incidents/_search?query=:query} : search for the incident corresponding
     * to the query.
     *
     * @param query the query of the incident search.
     * @param pageable the pagination information.
     * @return the result of the search.
     */
    @GetMapping("/_search")
    public ResponseEntity<List<Incident>> searchIncidents(
        @RequestParam("query") String query,
        @org.springdoc.core.annotations.ParameterObject Pageable pageable
    ) {
        LOG.debug("REST request to search for a page of Incidents for query {}", query);
        try {
            Page<Incident> page = incidentSearchRepository.search(query, pageable);
            HttpHeaders headers = PaginationUtil.generatePaginationHttpHeaders(ServletUriComponentsBuilder.fromCurrentRequest(), page);
            return ResponseEntity.ok().headers(headers).body(page.getContent());
        } catch (RuntimeException e) {
            throw ElasticsearchExceptionMapper.mapException(e);
        }
    }
}
