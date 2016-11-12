import React, { Component } from 'react';
import logo from './logo.svg';
import './App.css';
import { Button, Table, ControlLabel, FormControl, FormGroup, HelpBlock } from 'react-bootstrap';
import { withRouter } from 'react-router';
import { WithData, List } from './General';

// General container for all Checks routes. Dont put anything here.
export function Checks(props) {
  return (
    <div>
      {props.children}
    </div>
  )
}

export function ChecksListWithData() {
  return (
    <WithData resource="checks">
      <ChecksList />
    </WithData>
  )
}

export function ChecksList({ data }) {
  let columns = ["id", "check_type", "check_metadata"];
  let columnNames = ["ID", "Check Type", "Check Metadata"];

  return (
    <List data={data} columnNames={columnNames} columns={columns} baseResource="checks"/>
  );
}

ChecksList.propTypes = {
  data: React.PropTypes.arrayOf(React.PropTypes.shape({
     id: React.PropTypes.number.isRequired,
     check_type: React.PropTypes.string.isRequired,
     check_metadata: React.PropTypes.object.isRequired
   })).isRequired
}

ChecksList.defaultProps = {
  data: []
};


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


