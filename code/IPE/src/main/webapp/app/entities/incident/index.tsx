import React from 'react';
import { Route } from 'react-router';

import ErrorBoundaryRoutes from 'app/shared/error/error-boundary-routes';

import Incident from './incident';
import IncidentDetail from './incident-detail';
import IncidentUpdate from './incident-update';
import IncidentDeleteDialog from './incident-delete-dialog';

const IncidentRoutes = () => (
  <ErrorBoundaryRoutes>
    <Route index element={<Incident />} />
    <Route path="new" element={<IncidentUpdate />} />
    <Route path=":id">
      <Route index element={<IncidentDetail />} />
      <Route path="edit" element={<IncidentUpdate />} />
      <Route path="delete" element={<IncidentDeleteDialog />} />
    </Route>
  </ErrorBoundaryRoutes>
);

export default IncidentRoutes;
