import React, { Component } from 'react';
import './App.css';
import { ControlLabel, FormControl, FormGroup } from 'react-bootstrap';
import { WithData, List, ResourceForm, SingleFieldElement } from './General';

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

  handleMetadataChange(type, e) {
    let newState = { check_metadata: {} }
    newState.check_metadata[type] = e.target.value;
    this.setState(newState);
  }

  handleTypeChange(e) {
    this.setState({ check_type: e.target.value });
  }

  render() {
    let controlId = "column";
    let onChange = this.handleMetadataChange.bind(this, "column");
    let placeholder = "Enter column name";
    let label = "Column to Check";
    let value = this.state.check_metadata.column;

    if(this.state.check_type === 'CheckType.column_comparison') {
      controlId = "expression";
      label = "Expression";
      value = this.state.check_metadata.expression;
      onChange = this.handleMetadataChange.bind(this, "expression");
      placeholder = "Please enter a SQL expression using one or more columns in the table that evaluates to true. Eg. x != y"
    } 

    return (
      <ResourceForm data={this.state} baseResource={this.props.baseResource}>
        <FormGroup controlId="checkType">
          <ControlLabel>Check Type</ControlLabel>
          <FormControl componentClass="select" value={this.state.check_type} onChange={this.handleTypeChange.bind(this)}>
            <option value="CheckType.uniqueness">Uniqueness</option>
            <option value="CheckType.null">Null</option>
            <option value="CheckType.date_gap">DateGap</option>
            <option value="CheckType.column_comparison">Column Comparison</option>
          </FormControl>
        </FormGroup>

        <SingleFieldElement 
          label={label}
          value={value}
          controlId={controlId}
          onChange={onChange}
          placeholder={placeholder}
        />
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


