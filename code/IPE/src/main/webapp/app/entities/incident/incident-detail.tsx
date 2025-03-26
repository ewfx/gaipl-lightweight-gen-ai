import React, { useEffect } from 'react';
import { Link, useParams } from 'react-router-dom';
import { Button, Col, Row } from 'reactstrap';
import { TextFormat } from 'react-jhipster';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';

import { APP_DATE_FORMAT } from 'app/config/constants';
import { useAppDispatch, useAppSelector } from 'app/config/store';

import { getEntity } from './incident.reducer';

export const IncidentDetail = () => {
  const dispatch = useAppDispatch();

  const { id } = useParams<'id'>();

  useEffect(() => {
    dispatch(getEntity(id));
  }, []);

  const incidentEntity = useAppSelector(state => state.incident.entity);
  return (
    <Row>
      <Col md="8">
        <h2 data-cy="incidentDetailsHeading">Incident</h2>
        <dl className="jh-entity-details">
          <dt>
            <span id="id">ID</span>
          </dt>
          <dd>{incidentEntity.id}</dd>
          <dt>
            <span id="incidentnum">Incidentnum</span>
          </dt>
          <dd>{incidentEntity.incidentnum}</dd>
          <dt>
            <span id="shortDescription">Short Description</span>
          </dt>
          <dd>{incidentEntity.shortDescription}</dd>
          <dt>
            <span id="descrption">Descrption</span>
          </dt>
          <dd>{incidentEntity.descrption}</dd>
          <dt>
            <span id="status">Status</span>
          </dt>
          <dd>{incidentEntity.status}</dd>
          <dt>
            <span id="priority">Priority</span>
          </dt>
          <dd>{incidentEntity.priority}</dd>
          <dt>
            <span id="openedAt">Opened At</span>
          </dt>
          <dd>{incidentEntity.openedAt ? <TextFormat value={incidentEntity.openedAt} type="date" format={APP_DATE_FORMAT} /> : null}</dd>
          <dt>
            <span id="resolvedAt">Resolved At</span>
          </dt>
          <dd>
            {incidentEntity.resolvedAt ? <TextFormat value={incidentEntity.resolvedAt} type="date" format={APP_DATE_FORMAT} /> : null}
          </dd>
        </dl>
        <Button tag={Link} to="/incident" replace color="info" data-cy="entityDetailsBackButton">
          <FontAwesomeIcon icon="arrow-left" /> <span className="d-none d-md-inline">Back</span>
        </Button>
        &nbsp;
        <Button tag={Link} to={`/incident/${incidentEntity.id}/edit`} replace color="primary">
          <FontAwesomeIcon icon="pencil-alt" /> <span className="d-none d-md-inline">Edit</span>
        </Button>
      </Col>
    </Row>
  );
};

export default IncidentDetail;
