import React, { Component } from 'react';
import logo from './logo.svg';
import './App.css';
import { Button, Table, ControlLabel, FormControl, FormGroup, HelpBlock } from 'react-bootstrap';
import { WithData, List, ResourceForm } from './General';

// General container for all Checks routes. Dont put anything here.
export function Checks(props) {
  return (
    <div>
      {props.children}
    </div>
  )
}

export function ChecksList(props) {
  let columns = ["id", "check_type", "check_metadata"];
  let columnNames = ["ID", "Check Type", "Check Metadata"];

  return (
    <List columnNames={columnNames} columns={columns} {...props}/>
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


export function ChecksListWithData() {
  return (
    <WithData baseResource="checks">
      <ChecksList />
    </WithData>
  )
}


class CheckForm extends Component {

  constructor(props) {
    super(props);
    this.state = props.data;
  }

  componentWillReceiveProps(nextProps) {
    this.setState(nextProps.data);
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

  render() {

    return (
      <ResourceForm data={this.state} baseResource={this.props.baseResource}>
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
      </ResourceForm>
    )
  }
}

CheckForm.propTypes = {
  data: React.PropTypes.shape({
     id: React.PropTypes.oneOfType([React.PropTypes.number, React.PropTypes.string]).isRequired,
     check_type: React.PropTypes.string.isRequired,
     check_metadata: React.PropTypes.object.isRequired
   })
}

function CheckFormWithData({params}) {
  return (
    <WithData baseResource={"checks/" + params.id}>
      <CheckForm />
    </WithData>

  )
}
export { CheckFormWithData };


