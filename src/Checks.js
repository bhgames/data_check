import React, { Component } from 'react';
import logo from './logo.svg';
import './App.css';
import { Button, Table, ControlLabel, FormControl, FormGroup, HelpBlock } from 'react-bootstrap';
import { LinkContainer } from 'react-router-bootstrap';
import { withRouter } from 'react-router';

export function Checks(props) {
  return (
    <div>
      {props.children}
    </div>
  )
}

export class ChecksListWithData extends Component {

  constructor(props) {
    super(props);
    this.state = { checks: [] };
    let headers = new Headers();
    headers.append('Content-Type', 'application/json');

    let params = { method: 'GET',
                   headers: headers,
                   mode: 'cors'
                 };

    let get = new Request('http://localhost:5000/checks');
    let that = this;

    fetch(get, params).then(function(response) {
      return response.json();
    }).then(function(json) {
      that.setState({ checks: json })
    })

  }

  render() {
    return (
      <div>
        <ChecksList checks={this.state.checks}/>
      </div>
    )
  }

}

export function ChecksList({ checks }) {
  return (
    <div>

      <LinkContainer to={'/checks/new/edit'}>
        <Button bsStyle="primary">New</Button>
      </LinkContainer>

      <Table responsive striped bordered condensed hover>
        <thead>
          <tr>
            <th>Check ID</th>
            <th>Check Type</th>
            <th>Check Metadata</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {checks.map(check => 
            <tr key={check.id}>
              <td>{check.id}</td>
              <td>{check.check_type}</td>
              <td>{check.check_metadata.column}</td>
              <td>
                <LinkContainer to={'/checks/' + check.id + '/edit'}>
                  <Button>Edit</Button>
                </LinkContainer>
                <Button>Delete</Button>
              </td>
            </tr>
          )}
        </tbody>
      </Table> 
    </div>
  );
}

ChecksList.propTypes = {
  checks: React.PropTypes.arrayOf(React.PropTypes.shape({
     id: React.PropTypes.number.isRequired,
     check_type: React.PropTypes.string.isRequired,
     check_metadata: React.PropTypes.object.isRequired
   })).isRequired
}


class UnwrappedCheckForm extends Component {

  constructor(props) {
    super(props)
    this.state = {
      check_metadata: {
        column: ''
      },
      check_type: 'CheckType.uniqueness'
    };

    if(props.params.id != "new") {
      let headers = new Headers();
      headers.append('Content-Type', 'application/json');

      let params = { method: 'GET',
                     headers: headers,
                     mode: 'cors'
                   };

      let get = new Request('http://localhost:5000/checks/' + props.params.id);
      let that = this;

      fetch(get, params).then(function(response) {
        return response.json();
      }).then(function(json) {
        that.setState(json);
      })
    }

  }


  getValidationState() {
    const length = this.state.check_metadata.column.length;
    if (length >= 1) return 'success';
    else if (length > 0) return 'error';
  }

  handleChange(e) {
    this.setState({ check_metadata: { column: e.target.value } });
  }

  handleTypeChange(e) {
    this.setState({ check_type: e.target.value });
  }

  submit(e) {
    e.preventDefault();
    let headers = new Headers();
    headers.append('Content-Type', 'application/json');

    let params = { method: 'POST',
                   headers: headers,
                   mode: 'cors',
                   body: JSON.stringify(this.state)
                 };

    let add = "";

    if(this.props.params.id != "new") {
      add = "/" + this.props.params.id;
      params.method = 'PUT';
    }

    let post = new Request('http://localhost:5000/checks' + add);
    let that = this;

    fetch(post,params).then(function(response) {
      if(response.ok) {
        that.props.router.push('/checks');
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
          <FormControl componentClass="select" value={this.state.check_type} onChange={this.handleTypeChange.bind(this)}>
            <option value="CheckType.uniqueness">Uniqueness</option>
            <option value="CheckType.null">Null</option>
            <option value="CheckType.date_gap">DateGap</option>
          </FormControl>
        </FormGroup>

         <FormGroup
          controlId="columnType"
          validationState={this.getValidationState()}
        >
          <ControlLabel>Column to Check</ControlLabel>
          <FormControl
            type="text"
            value={this.state.check_metadata.column}
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

UnwrappedCheckForm.propTypes = {
  params: React.PropTypes.shape({
     id: React.PropTypes.string.isRequired
   }).isRequired
}

let CheckForm = withRouter(UnwrappedCheckForm);
export { CheckForm };


