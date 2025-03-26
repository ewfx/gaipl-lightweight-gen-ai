package com.hackathon.ipe.domain;

import jakarta.persistence.*;
import java.io.Serializable;
import java.time.Instant;

/**
 * A Incident.
 */
@Entity
@Table(name = "incident")
@org.springframework.data.elasticsearch.annotations.Document(indexName = "incident")
@SuppressWarnings("common-java:DuplicatedBlocks")
public class Incident implements Serializable {

    private static final long serialVersionUID = 1L;

    @Id
    @GeneratedValue(strategy = GenerationType.SEQUENCE, generator = "sequenceGenerator")
    @SequenceGenerator(name = "sequenceGenerator")
    @Column(name = "id")
    private Long id;

    @Column(name = "incidentnum")
    @org.springframework.data.elasticsearch.annotations.Field(type = org.springframework.data.elasticsearch.annotations.FieldType.Text)
    private String incidentnum;

    @Column(name = "short_description")
    @org.springframework.data.elasticsearch.annotations.Field(type = org.springframework.data.elasticsearch.annotations.FieldType.Text)
    private String shortDescription;

    @Column(name = "descrption")
    @org.springframework.data.elasticsearch.annotations.Field(type = org.springframework.data.elasticsearch.annotations.FieldType.Text)
    private String descrption;

    @Column(name = "status")
    @org.springframework.data.elasticsearch.annotations.Field(type = org.springframework.data.elasticsearch.annotations.FieldType.Text)
    private String status;

    @Column(name = "priority")
    @org.springframework.data.elasticsearch.annotations.Field(type = org.springframework.data.elasticsearch.annotations.FieldType.Text)
    private String priority;

    @Column(name = "opened_at")
    private Instant openedAt;

    @Column(name = "resolved_at")
    private Instant resolvedAt;

    // jhipster-needle-entity-add-field - JHipster will add fields here

    public Long getId() {
        return this.id;
    }

    public Incident id(Long id) {
        this.setId(id);
        return this;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public String getIncidentnum() {
        return this.incidentnum;
    }

    public Incident incidentnum(String incidentnum) {
        this.setIncidentnum(incidentnum);
        return this;
    }

    public void setIncidentnum(String incidentnum) {
        this.incidentnum = incidentnum;
    }

    public String getShortDescription() {
        return this.shortDescription;
    }

    public Incident shortDescription(String shortDescription) {
        this.setShortDescription(shortDescription);
        return this;
    }

    public void setShortDescription(String shortDescription) {
        this.shortDescription = shortDescription;
    }

    public String getDescrption() {
        return this.descrption;
    }

    public Incident descrption(String descrption) {
        this.setDescrption(descrption);
        return this;
    }

    public void setDescrption(String descrption) {
        this.descrption = descrption;
    }

    public String getStatus() {
        return this.status;
    }

    public Incident status(String status) {
        this.setStatus(status);
        return this;
    }

    public void setStatus(String status) {
        this.status = status;
    }

    public String getPriority() {
        return this.priority;
    }

    public Incident priority(String priority) {
        this.setPriority(priority);
        return this;
    }

    public void setPriority(String priority) {
        this.priority = priority;
    }

    public Instant getOpenedAt() {
        return this.openedAt;
    }

    public Incident openedAt(Instant openedAt) {
        this.setOpenedAt(openedAt);
        return this;
    }

    public void setOpenedAt(Instant openedAt) {
        this.openedAt = openedAt;
    }

    public Instant getResolvedAt() {
        return this.resolvedAt;
    }

    public Incident resolvedAt(Instant resolvedAt) {
        this.setResolvedAt(resolvedAt);
        return this;
    }

    public void setResolvedAt(Instant resolvedAt) {
        this.resolvedAt = resolvedAt;
    }

    // jhipster-needle-entity-add-getters-setters - JHipster will add getters and setters here

    @Override
    public boolean equals(Object o) {
        if (this == o) {
            return true;
        }
        if (!(o instanceof Incident)) {
            return false;
        }
        return getId() != null && getId().equals(((Incident) o).getId());
    }

    @Override
    public int hashCode() {
        // see https://vladmihalcea.com/how-to-implement-equals-and-hashcode-using-the-jpa-entity-identifier/
        return getClass().hashCode();
    }

    // prettier-ignore
    @Override
    public String toString() {
        return "Incident{" +
            "id=" + getId() +
            ", incidentnum='" + getIncidentnum() + "'" +
            ", shortDescription='" + getShortDescription() + "'" +
            ", descrption='" + getDescrption() + "'" +
            ", status='" + getStatus() + "'" +
            ", priority='" + getPriority() + "'" +
            ", openedAt='" + getOpenedAt() + "'" +
            ", resolvedAt='" + getResolvedAt() + "'" +
            "}";
    }
}
