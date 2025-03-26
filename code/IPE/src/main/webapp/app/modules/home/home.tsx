import './home.scss';

import React from 'react';
import { Link } from 'react-router-dom';

import { Alert, Col, Row } from 'reactstrap';

import { useAppSelector } from 'app/config/store';

export const Home = () => {
  const account = useAppSelector(state => state.authentication.account);

  return (
    <Row>
      <Col md="3" className="pad">
        <span className="hipster rounded" />
      </Col>
      <Col md="9">
        <h1 className="display-4">Welcome, Support Hipster!</h1>
        <p className="lead">Agents for your Assistance!</p>
        {account?.login ? (
          <div>
            <Alert color="success">You are logged in as user &quot;{account.login}&quot;.</Alert>
          </div>
        ) : (
          <div>
            <Alert color="warning">
              If you want to
              <span>&nbsp;</span>
              <Link to="/login" className="alert-link">
                sign in
              </Link>
              , you can try the default accounts:
              <br />
              User (login=&quot;user&quot; and password=&quot;user&quot;).
            </Alert>
          </div>
        )}
        <p>AI Enabled Integrated Environment with below features:</p>

        <ul>
          <li>
            <a target="_blank" rel="noopener noreferrer">
              Natural Language Based Incidents Search
            </a>
          </li>
          <li>
            <a target="_blank" rel="noopener noreferrer">
              Personalisable Assitant.
            </a>
          </li>
          <li>
            <a target="_blank" rel="noopener noreferrer">
              Context Aware Incident Assistant
            </a>
          </li>
          <li>
            <a target="_blank" rel="noopener noreferrer">
              Easily Expandable, Standards based Open Architecture
            </a>
          </li>
        </ul>
      </Col>
    </Row>
  );
};

export default Home;
