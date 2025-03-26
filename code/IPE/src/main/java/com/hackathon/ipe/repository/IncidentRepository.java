package com.hackathon.ipe.repository;

import com.hackathon.ipe.domain.Incident;
import org.springframework.data.jpa.repository.*;
import org.springframework.stereotype.Repository;

/**
 * Spring Data JPA repository for the Incident entity.
 */
@SuppressWarnings("unused")
@Repository
public interface IncidentRepository extends JpaRepository<Incident, Long> {}
