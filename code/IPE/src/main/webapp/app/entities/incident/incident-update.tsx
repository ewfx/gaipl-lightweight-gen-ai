import React, { useEffect } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { Button, Col, Row } from 'reactstrap';
import { ValidatedField, ValidatedForm } from 'react-jhipster';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';

import { convertDateTimeFromServer, convertDateTimeToServer, displayDefaultDateTime } from 'app/shared/util/date-utils';
import { useAppDispatch, useAppSelector } from 'app/config/store';

import { createEntity, getEntity, updateEntity } from './incident.reducer';

export const IncidentUpdate = () => {
  const dispatch = useAppDispatch();

  const navigate = useNavigate();

  const { id } = useParams<'id'>();
  const isNew = id === undefined;

  const incidentEntity = useAppSelector(state => state.incident.entity);
  const loading = useAppSelector(state => state.incident.loading);
  const updating = useAppSelector(state => state.incident.updating);
  const updateSuccess = useAppSelector(state => state.incident.updateSuccess);

  const handleClose = () => {
    navigate('/incident');
  };

  useEffect(() => {
    if (!isNew) {
      dispatch(getEntity(id));
    }
  }, []);

  useEffect(() => {
    if (updateSuccess) {
      handleClose();
    }
  }, [updateSuccess]);

  const saveEntity = values => {
    if (values.id !== undefined && typeof values.id !== 'number') {
      values.id = Number(values.id);
    }
    values.openedAt = convertDateTimeToServer(values.openedAt);
    values.resolvedAt = convertDateTimeToServer(values.resolvedAt);

    const entity = {
      ...incidentEntity,
      ...values,
    };

    if (isNew) {
      dispatch(createEntity(entity));
    } else {
      dispatch(updateEntity(entity));
    }
  };

  const defaultValues = () =>
    isNew
      ? {
          openedAt: displayDefaultDateTime(),
          resolvedAt: displayDefaultDateTime(),
        }
      : {
          ...incidentEntity,
          openedAt: convertDateTimeFromServer(incidentEntity.openedAt),
          resolvedAt: convertDateTimeFromServer(incidentEntity.resolvedAt),
        };

  return (
    <div>
      <Row className="justify-content-center">
        <Col md="8">
          <h2 id="ipeApp.incident.home.createOrEditLabel" data-cy="IncidentCreateUpdateHeading">
            Create or edit a Incident
          </h2>
        </Col>
      </Row>
      <Row className="justify-content-center">
        <Col md="8">
          {loading ? (
            <p>Loading...</p>
          ) : (
            <ValidatedForm defaultValues={defaultValues()} onSubmit={saveEntity}>
              {!isNew ? <ValidatedField name="id" required readOnly id="incident-id" label="ID" validate={{ required: true }} /> : null}
              <ValidatedField label="Incidentnum" id="incident-incidentnum" name="incidentnum" data-cy="incidentnum" type="text" />
              <ValidatedField
                label="Short Description"
                id="incident-shortDescription"
                name="shortDescription"
                data-cy="shortDescription"
                type="text"
              />
              <ValidatedField label="Descrption" id="incident-descrption" name="descrption" data-cy="descrption" type="text" />
              <ValidatedField label="Status" id="incident-status" name="status" data-cy="status" type="text" />
              <ValidatedField label="Priority" id="incident-priority" name="priority" data-cy="priority" type="text" />
              <ValidatedField
                label="Opened At"
                id="incident-openedAt"
                name="openedAt"
                data-cy="openedAt"
                type="datetime-local"
                placeholder="YYYY-MM-DD HH:mm"
              />
              <ValidatedField
                label="Resolved At"
                id="incident-resolvedAt"
                name="resolvedAt"
                data-cy="resolvedAt"
                type="datetime-local"
                placeholder="YYYY-MM-DD HH:mm"
              />
              <Button tag={Link} id="cancel-save" data-cy="entityCreateCancelButton" to="/incident" replace color="info">
                <FontAwesomeIcon icon="arrow-left" />
                &nbsp;
                <span className="d-none d-md-inline">Back</span>
              </Button>
              &nbsp;
              <Button color="primary" id="save-entity" data-cy="entityCreateSaveButton" type="submit" disabled={updating}>
                <FontAwesomeIcon icon="save" />
                &nbsp; Save
              </Button>
            </ValidatedForm>
          )}
        </Col>
      </Row>
    </div>
  );
};

export default IncidentUpdate;
