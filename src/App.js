import React, { Component } from 'react';
import logo from './logo.svg';
import './App.css';
import { Navbar, NavItem, NavDropdown, MenuItem, Nav } from 'react-bootstrap';
import { IndexLinkContainer, LinkContainer } from 'react-router-bootstrap';
import {  Link } from 'react-router';

class App extends Component {
  // Put sidebar here.
  render() {
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
            <IndexLinkContainer to={`/`}>
              <NavItem eventKey={1}>Recent</NavItem>
            </IndexLinkContainer>
            <LinkContainer to={`/checks`}>
              <NavItem eventKey={2}>Checks</NavItem>
            </LinkContainer>
            <LinkContainer to={`/rules`}>
              <NavItem eventKey={3}>Rules</NavItem>
            </LinkContainer>
          </Nav>
        </Navbar.Collapse>
      </Navbar>

      {this.props.children}
    </div>
    );
  }
}

export default App;
