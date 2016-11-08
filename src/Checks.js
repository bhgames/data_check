import React, { Component } from 'react';
import logo from './logo.svg';
import './App.css';
import { Button, Table, ControlLabel, FormControl, FormGroup, HelpBlock } from 'react-bootstrap';
import { LinkContainer } from 'react-router-bootstrap';

export function Checks(props) {
  return (
    <div>
      {props.children}
    </div>
  )
}

export function ChecksList() {
  return (
    <div>

      <LinkContainer to={'/checks/new'}>
        <Button bsStyle="primary">New</Button>
      </LinkContainer>

      <Table responsive striped bordered condensed hover>
        <thead>
          <tr>
            <th>Check ID</th>
            <th>Check Type</th>
            <th>Check Metadata</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>1</td>
            <td>Uniqueness</td>
            <td> column: "id" </td>
          </tr>
        </tbody>
      </Table> 
    </div>
  );
}

export class NewCheckForm extends Component {

  constructor(props) {
    super(props);
    this.state = {
      column: '',
      checkType: 'Uniqueness'
    }
  }

  getValidationState() {
    const length = this.state.column.length;
    if (length >= 1) return 'success';
    else if (length > 0) return 'error';
  }

  handleChange(e) {
    this.setState({ column: e.target.value });
  }

  handleTypeChange(e) {
    this.setState({ checkType: e.target.value });
  }

  submit(e) {
    e.preventDefault();
    let headers = new Headers();
    headers.append('Content-Type', 'application/json');

    let params = { method: 'POST',
                   headers: headers,
                   mode: 'cors',
                   body: {
                    check_type: this.state.checkType,
                    check_metadata: {
                      column: this.state.column
                    }
                   } 
                 };

    let post = new Request('http://localhost:5000/checks');

    fetch(post,params).then(function(response) {
      if(response.ok) {
        console.log("yay");
      } else {
        console.log(response);
      }
    })

  }

  render() {

    return (
      <form onSubmit={this.submit.bind(this)}>
        <FormGroup controlId="checkType">
          <ControlLabel>Check Type</ControlLabel>
          <FormControl componentClass="select" value={this.state.checkType} onChange={this.handleTypeChange.bind(this)}>
            <option value="Uniqueness">Uniqueness</option>
            <option value="Null">Null</option>
            <option value="DateGap">DateGap</option>
          </FormControl>
        </FormGroup>

         <FormGroup
          controlId="columnType"
          validationState={this.getValidationState()}
        >
          <ControlLabel>Column to Check</ControlLabel>
          <FormControl
            type="text"
            value={this.state.column}
            placeholder="Enter text"
            onChange={this.handleChange.bind(this)}
          />
          <FormControl.Feedback />
        </FormGroup>

        <Button type="submit">
          Submit
        </Button>
      </form>
    )
  }
}


