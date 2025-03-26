import React from 'react';

import ErrorBoundaryRoutes from 'app/shared/error/error-boundary-routes';

import Incident from './incident';
import { Route } from 'react-router-dom';

/* jhipster-needle-add-route-import - JHipster will add routes here */

export default () => {
  return (
    <div>
      <ErrorBoundaryRoutes>
        {/* prettier-ignore */}
        <Route path="incident/*" element={<Incident />} />
        {/* jhipster-needle-add-route-path - JHipster will add routes here */}
      </ErrorBoundaryRoutes>
    </div>
  );
};
