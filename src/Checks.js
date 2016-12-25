import React, { Component } from 'react';
import './App.css';
import { ControlLabel, FormControl, FormGroup } from 'react-bootstrap';
import { WithData, List, ResourceForm, SingleFieldElement } from './General';

// General container for all Checks routes. Dont put anything here.
export function Checks(props) {
  return props.children
}

export function ChecksList(props) {
  let columns = ["id", "check_name", "check_type", "check_metadata"];
  let columnNames = ["ID", "Name", "Type", "Metadata"];

  return (
    <List columnNames={columnNames} columns={columns} {...props}/>
  );
}

ChecksList.propTypes = {
  data: React.PropTypes.arrayOf(React.PropTypes.shape({
    id: React.PropTypes.number.isRequired,
    check_name: React.PropTypes.string.isRequired,
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

function ForeignKeyCheck({ fkColPattern, fkTableIdPattern, handleMetadataChange }) {
  let handler = (key, e) => handleMetadataChange(key, e);
  return (
    <FormGroup controlId="foreignKeyCheck" key="foreignKeyCheck">
      <SingleFieldElement 
          label='Foreign Key Column Regex'
          value={fkColPattern}
          controlId='fkColPattern'
          onChange={handler.bind(null, "fk_col_pattern")}
          placeholder='(.*)_id'
          key='fkColPattern'
        />
        <SingleFieldElement 
          label='Foreign Table ID Regex'
          value={fkTableIdPattern}
          controlId='fkTableIdPattern'
          onChange={handler.bind(null, "fk_table_id_pattern")}
          placeholder='^id$'
          key='fkTableIdPattern'
        />
    </FormGroup>
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
    // FIXME: This modifies state directly because check_metadata still references
    // the same object that's in the state.
    let newState = { check_metadata: this.state.check_metadata };
    newState.check_metadata[type] = e.target.value;
    this.setState(newState);
  }

  handleTypeChange(e) {
    this.setState({ check_type: e.target.value });
  }

  handleNameChange(e) {
    this.setState({ check_name: e.target.value });
  }

  render() {
    let controlId = "column";
    let onChange = this.handleMetadataChange.bind(this, "column");
    let placeholder = "Enter column name";
    let label = "Column to Check";
    let value = this.state.check_metadata.column;
    let fields = [];

    if(this.state.check_type === 'CheckType.column_comparison') {
      controlId = "expression";
      label = "Expression";
      value = this.state.check_metadata.expression;
      onChange = this.handleMetadataChange.bind(this, "expression");
      placeholder = "Please enter a SQL expression using one or more columns in the table that evaluates to true. Eg. x != y"
    } else if(this.state.check_type === 'CheckType.id_gap') {
      fields.push(<SingleFieldElement 
          label='Choose a range threshold'
          value={this.state.check_metadata.threshold}
          controlId='threshold'
          onChange={this.handleMetadataChange.bind(this, "threshold")}
          placeholder='If you want to catch a missing gap of id = 1, followed by id = 5, threshold should be 5'
          key='threshold'
        />);
    } 

    if(this.state.check_type == 'CheckType.foreign_key') {
      fields.push(<ForeignKeyCheck handleMetadataChange={this.handleMetadataChange.bind(this)} 
                                   fkColPattern={this.state.check_metadata.fk_col_pattern} 
                                   fkTableIdPattern={this.state.check_metadata.fk_table_id_pattern} />)
    } else {
      // TODO turn other field configs into their own components a la FK Check.
      fields.push(<SingleFieldElement 
                      label={label}
                      value={value}
                      controlId={controlId}
                      onChange={onChange}
                      placeholder={placeholder}
                      key='control'
                  />);
    }

    return (
      <ResourceForm data={this.state} baseResource={this.props.baseResource}>
        <h2>New Check</h2>
        <SingleFieldElement
            label="Name"
            value={this.state.check_name}
            controlId="checkName"
            onChange={this.handleNameChange.bind(this)}
            placeholder="Enter a name for your check"
        />

        <FormGroup controlId="checkType">
          <ControlLabel>Type</ControlLabel>
          <FormControl componentClass="select" value={this.state.check_type} onChange={this.handleTypeChange.bind(this)}>
            <option value="CheckType.uniqueness">Uniqueness</option>
            <option value="CheckType.null">Null</option>
            <option value="CheckType.date_gap">DateGap</option>
            <option value="CheckType.column_comparison">Column Comparison</option>
            <option value="CheckType.id_gap">ID Gap</option>
            <option value="CheckType.foreign_key">Foreign Key Check</option>
          </FormControl>
        </FormGroup>

        {fields}
        
      </ResourceForm>
    )
  }
}

CheckForm.propTypes = {
  data: React.PropTypes.shape({
    id: React.PropTypes.oneOfType([React.PropTypes.number, React.PropTypes.string]).isRequired,
    check_name: React.PropTypes.string.isRequired,
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


