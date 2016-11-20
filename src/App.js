import React, { Component } from 'react';
import './App.css';
import { Navbar, NavItem, Nav } from 'react-bootstrap';
import { IndexLinkContainer, LinkContainer } from 'react-router-bootstrap';

export function IndexComponent() {
  return <p>No home page yet.</p>
}

export function App({children}) {
  // Put sidebar here.
  return (
  <div>
    <Navbar inverse collapseOnSelect>
      <Navbar.Header>
        <Navbar.Brand>
          <a href="#">Data Check</a>
        </Navbar.Brand>
        <Navbar.Toggle />
      </Navbar.Header>
      <Navbar.Collapse>
        <Nav>
          <IndexLinkContainer to={`/job_runs`}>
            <NavItem eventKey={1}>Job Runs</NavItem>
          </IndexLinkContainer>
          <LinkContainer to={`/checks`}>
            <NavItem eventKey={2}>Checks</NavItem>
          </LinkContainer>
          <LinkContainer to={`/rules`}>
            <NavItem eventKey={3}>Rules</NavItem>
          </LinkContainer>
          <LinkContainer to={`/job_templates`}>
            <NavItem eventKey={4}>Job Templates</NavItem>
          </LinkContainer>
          <LinkContainer to={`/data_sources`}>
            <NavItem eventKey={5}>Data Sources</NavItem>
          </LinkContainer>
        </Nav>
      </Navbar.Collapse>
    </Navbar>

    {children}
  </div>
  );
  
}

export default App;
