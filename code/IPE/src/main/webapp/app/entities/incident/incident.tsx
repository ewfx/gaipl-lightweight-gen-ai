import React, { useEffect, useState } from 'react';
import InfiniteScroll from 'react-infinite-scroll-component';
import { Link, useLocation } from 'react-router-dom';
import { Button, Col, Form, FormGroup, Input, InputGroup, Row, Table } from 'reactstrap';
import { TextFormat, getPaginationState } from 'react-jhipster';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faSort, faSortDown, faSortUp, faSearch, faTrash, faEye } from '@fortawesome/free-solid-svg-icons';
import { APP_DATE_FORMAT } from 'app/config/constants';
import { ASC, DESC, ITEMS_PER_PAGE } from 'app/shared/util/pagination.constants';
import { overridePaginationStateWithQueryParams } from 'app/shared/util/entity-utils';
import { useAppDispatch, useAppSelector } from 'app/config/store';
import { getEntities, reset, searchEntities } from './incident.reducer';

declare global {
  interface Window {
    mountChainlitWidget?: (config: any) => void;
    sendChainlitMessage?: (msg: { type: string; output: string }) => void;
  }
}

export const Incident = () => {
  const dispatch = useAppDispatch();
  const pageLocation = useLocation();

  // ✅ Inject Chainlit Copilot script once
  if (typeof window !== 'undefined') {
    const scriptId = 'chainlit-widget-script';
    if (!document.getElementById(scriptId)) {
      const script = document.createElement('script');
      script.id = scriptId;
      script.src = 'http://localhost:8000/copilot/index.js';
      script.async = true;
      script.onload = () => {
        console.warn('✅ Chainlit Copilot script loaded');

        // Wait for the widget to initialize
        setTimeout(() => {
          window.mountChainlitWidget?.({
            chainlitServer: 'http://localhost:8000',
            defaultOpen: false,
            theme: 'light',
            chatProfile: { name: 'Incident Assistant' },
          });

          // Wait slightly longer, then click the launcher icon to trigger the widget initialization
          setTimeout(() => {
            const launcher = document.querySelector('chainlit-launcher');
            const button = launcher?.shadowRoot?.querySelector('button');

            if (button) {
              button.click(); // Open it
              console.warn('📢 Opened Chainlit Copilot to trigger mounting');

              // Then minimize it after 2 seconds
              setTimeout(() => {
                button.click(); // Close it
                console.warn('🟡 Minimized Chainlit Copilot after preload');
              }, 2000);
            } else {
              console.warn('⚠️ Could not find Chainlit launcher button to auto-open');
            }
          }, 1000); // Delay after widget mount
        }, 500); // Delay after script load
      };

      document.body.appendChild(script);
    }
  }

  const [search, setSearch] = useState('');
  const [showAssistant, setShowAssistant] = useState(true);
  const [paginationState, setPaginationState] = useState(
    overridePaginationStateWithQueryParams(getPaginationState(pageLocation, ITEMS_PER_PAGE, 'id'), pageLocation.search),
  );
  const [sorting, setSorting] = useState(false);

  const incidentList = useAppSelector(state => state.incident.entities);
  const loading = useAppSelector(state => state.incident.loading);
  const links = useAppSelector(state => state.incident.links);
  const updateSuccess = useAppSelector(state => state.incident.updateSuccess);

  const getAllEntities = () => {
    if (search) {
      dispatch(
        searchEntities({
          query: search,
          page: paginationState.activePage - 1,
          size: paginationState.itemsPerPage,
          sort: `${paginationState.sort},${paginationState.order}`,
        }),
      );
    } else {
      dispatch(
        getEntities({
          page: paginationState.activePage - 1,
          size: paginationState.itemsPerPage,
          sort: `${paginationState.sort},${paginationState.order}`,
        }),
      );
    }
  };

  const resetAll = () => {
    dispatch(reset());
    setPaginationState({
      ...paginationState,
      activePage: 1,
    });
    dispatch(getEntities({}));
  };

  useEffect(() => {
    resetAll();
  }, []);

  useEffect(() => {
    const handleCopilotFn = (e: CustomEvent) => {
      const { name, args, callback } = e.detail;

      if (name === 'getVisibleIncidents') {
        console.warn('📥 Copilot requested visible incidents');

        // Collect all visible incidents on screen
        const incidents = document.querySelectorAll('[data-cy="entityTable"]');
        const data = Array.from(incidents).map(row => {
          const cells = row.querySelectorAll('td');
          return {
            id: cells[0]?.innerText.trim(),
            incidentnum: cells[1]?.innerText.trim(),
            shortDescription: cells[2]?.innerText.trim(),
            descrption: cells[3]?.innerText.trim(),
            status: cells[4]?.innerText.trim(),
            priority: cells[5]?.innerText.trim(),
            openedAt: cells[6]?.innerText.trim(),
            resolvedAt: cells[7]?.innerText.trim(),
          };
        });

        callback({ incidents: data });
      }
    };

    window.addEventListener('chainlit-call-fn', handleCopilotFn as EventListener);

    return () => {
      window.removeEventListener('chainlit-call-fn', handleCopilotFn as EventListener);
    };
  }, []);

  const startSearching = e => {
    if (search) {
      dispatch(reset());
      setPaginationState({
        ...paginationState,
        activePage: 1,
      });
      dispatch(
        searchEntities({
          query: search,
          page: paginationState.activePage - 1,
          size: paginationState.itemsPerPage,
          sort: `${paginationState.sort},${paginationState.order}`,
        }),
      );
    }
    e.preventDefault();
  };

  const clear = () => {
    dispatch(reset());
    setSearch('');
    setPaginationState({
      ...paginationState,
      activePage: 1,
    });
    dispatch(getEntities({}));
  };

  const handleSearch = event => setSearch(event.target.value);

  useEffect(() => {
    if (updateSuccess) {
      resetAll();
    }
  }, [updateSuccess]);

  useEffect(() => {
    getAllEntities();
  }, [paginationState.activePage]);

  const handleLoadMore = () => {
    if ((window as any).pageYOffset > 0) {
      setPaginationState({
        ...paginationState,
        activePage: paginationState.activePage + 1,
      });
    }
  };

  useEffect(() => {
    if (sorting) {
      getAllEntities();
      setSorting(false);
    }
  }, [sorting, search]);

  const sort = p => () => {
    dispatch(reset());
    setPaginationState({
      ...paginationState,
      activePage: 1,
      order: paginationState.order === ASC ? DESC : ASC,
      sort: p,
    });
    setSorting(true);
  };

  const getSortIconByFieldName = (fieldName: string) => {
    const sortFieldName = paginationState.sort;
    const order = paginationState.order;
    if (sortFieldName !== fieldName) {
      return faSort;
    }
    return order === ASC ? faSortUp : faSortDown;
  };

  useEffect(() => {
    const scriptId = 'chainlit-copilot-widget';

    // 1. Inject Chainlit Copilot script
    if (!document.getElementById(scriptId)) {
      const script = document.createElement('script');
      script.src = 'http://localhost:8000/copilot/index.js'; // ✅ this is the CORRECT file for widget
      script.async = true;
      script.id = scriptId;
      document.body.appendChild(script);
    }

    // 2. Optionally mount widget manually if you want to open/override behavior
    setTimeout(() => {
      window.mountChainlitWidget?.({
        chainlitServer: 'http://localhost:8000',
        defaultOpen: false,
        theme: 'light',
        chatProfile: {
          name: 'Incident Assistant',
        },
      });
    }, 1000); // wait for script to load
  }, []);

  return (
    <>
      <Row style={{ margin: 0 }}>
        {/* Collapsible Left Pane */}
        {showAssistant && (
          <Col
            md="3"
            style={{
              padding: 0,
              borderRight: '1px solid #ccc',
              height: '100vh',
              position: 'relative',
            }}
          >
            <Button
              size="sm"
              onClick={() => setShowAssistant(false)}
              style={{
                position: 'absolute',
                right: '10px',
                bottom: '90px',
                zIndex: 1000,
                background: '#343a40',
                border: 'none',
                borderRadius: '50%',
                width: '30px',
                height: '30px',
                padding: 0,
                fontSize: '16px',
              }}
            >
              &laquo;
            </Button>

            <iframe src="http://localhost:8000" title="Chainlit Assistant" style={{ width: '100%', height: '100%', border: 'none' }} />
          </Col>
        )}

        {/* Right Pane - Incident List */}
        <Col md={showAssistant ? '9' : '12'} style={{ padding: '1rem', position: 'relative' }}>
          {!showAssistant && (
            <Button
              size="sm"
              onClick={() => setShowAssistant(true)}
              style={{
                position: 'absolute',
                top: '10px',
                left: '10px',
                zIndex: 1000,
                background: '#343a40',
                border: 'none',
              }}
            >
              &raquo;
            </Button>
          )}

          <h2 id="incident-heading" data-cy="IncidentHeading" className="text-center mb-4">
            Incidents
          </h2>

          <Row>
            <Col sm="12">
              <Form onSubmit={startSearching}>
                <FormGroup>
                  <InputGroup>
                    <Input type="text" name="search" defaultValue={search} onChange={handleSearch} placeholder="Search" />
                    <Button className="input-group-addon">
                      <FontAwesomeIcon icon={faSearch} />
                    </Button>
                    <Button type="reset" className="input-group-addon" onClick={clear}>
                      <FontAwesomeIcon icon={faTrash} />
                    </Button>
                  </InputGroup>
                </FormGroup>
              </Form>
            </Col>
          </Row>

          <div className="table-responsive">
            <InfiniteScroll
              dataLength={incidentList ? incidentList.length : 0}
              next={handleLoadMore}
              hasMore={paginationState.activePage - 1 < links.next}
              loader={<div className="loader">Loading ...</div>}
            >
              {incidentList && incidentList.length > 0 ? (
                <Table responsive>
                  <thead>
                    <tr>
                      <th className="hand" onClick={sort('id')}>
                        ID <FontAwesomeIcon icon={getSortIconByFieldName('id')} />
                      </th>
                      <th className="hand" onClick={sort('incidentnum')}>
                        Incident Number <FontAwesomeIcon icon={getSortIconByFieldName('incidentnum')} />
                      </th>
                      <th className="hand" onClick={sort('shortDescription')}>
                        Short Description <FontAwesomeIcon icon={getSortIconByFieldName('shortDescription')} />
                      </th>
                      <th className="hand" onClick={sort('descrption')}>
                        Description <FontAwesomeIcon icon={getSortIconByFieldName('descrption')} />
                      </th>
                      <th className="hand" onClick={sort('status')}>
                        Status <FontAwesomeIcon icon={getSortIconByFieldName('status')} />
                      </th>
                      <th className="hand" onClick={sort('priority')}>
                        Priority <FontAwesomeIcon icon={getSortIconByFieldName('priority')} />
                      </th>
                      <th className="hand" onClick={sort('openedAt')}>
                        Opened At <FontAwesomeIcon icon={getSortIconByFieldName('openedAt')} />
                      </th>
                      <th className="hand" onClick={sort('resolvedAt')}>
                        Resolved At <FontAwesomeIcon icon={getSortIconByFieldName('resolvedAt')} />
                      </th>
                      <th />
                    </tr>
                  </thead>
                  <tbody>
                    {incidentList.map((incident, i) => (
                      <tr key={`entity-${i}`} data-cy="entityTable">
                        <td>
                          <Button tag={Link} to={`/incident/${incident.id}`} color="link" size="sm">
                            {incident.id}
                          </Button>
                        </td>
                        <td>{incident.incidentnum}</td>
                        <td>{incident.shortDescription}</td>
                        <td>{incident.descrption}</td>
                        <td>{incident.status}</td>
                        <td>{incident.priority}</td>
                        <td>{incident.openedAt ? <TextFormat type="date" value={incident.openedAt} format={APP_DATE_FORMAT} /> : null}</td>
                        <td>
                          {incident.resolvedAt ? <TextFormat type="date" value={incident.resolvedAt} format={APP_DATE_FORMAT} /> : null}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </Table>
              ) : (
                !loading && <div className="alert alert-warning">No Incidents found</div>
              )}
            </InfiniteScroll>
          </div>
        </Col>
      </Row>
    </>
  );
};

export default Incident;
