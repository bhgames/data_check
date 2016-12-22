import React, { Component } from 'react';
import './App.css';
import { ControlLabel, FormControl, FormGroup } from 'react-bootstrap';
import { ChecksList } from './Checks';
import { WithData, List, ResourceForm, HasManyAssociationFormElement, SingleFieldElement } from './General';

// General container for all Rules routes. Dont put anything here.
export function Rules(props) {
  return props.children;
}

export function RulesList(props) {
  let columns = ["id", "name", "condition", "conditional"];
  let columnNames = ["ID", "Name", "Condition", "Conditional"];

  return (
    <List columnNames={columnNames} columns={columns} {...props}/>
  );
}

RulesList.propTypes = {
  data: React.PropTypes.arrayOf(React.PropTypes.shape({
    id: React.PropTypes.number.isRequired,
    name: React.PropTypes.string.isRequired,
    condition: React.PropTypes.string.isRequired,
    conditional: React.PropTypes.object.isRequired
  })).isRequired
}

RulesList.defaultProps = {
  data: []
};


export function RulesListWithData() {
  return (
    <WithData baseResource="rules">
      <RulesList />
    </WithData>
  )
}


class RuleForm extends Component {

  constructor(props) {
    super(props);
    this.state = props.data;
  }

  componentWillReceiveProps(nextProps) {
    this.setState(nextProps.data);
  }

  handleConditionalChange(type, e) {
    let newCond = { conditional: {} };
    newCond.conditional[type] = e.target.value;
    this.setState(newCond);
  }

  handleTypeChange(e) {
    this.setState({ condition: e.target.value });
  }

  handleAssocChange(stateKey, newList) {
    let newState = {};
    newState[stateKey] = newList;
    this.setState(newState);
  }

  handleNameChange(e) {
    this.setState({ name: e.target.value });
  }

  render() {

    let controlId = "conditionalType";
    let onChange = this.handleConditionalChange.bind(this, "column");
    let placeholder = "Enter text";
    let label = "Column";
    let value = this.state.conditional.column;

    if(this.state.condition.match("table_name")) {
      label = "Pattern";
      value = this.state.conditional.pattern;
      onChange = this.handleConditionalChange.bind(this, "pattern");
      placeholder = "Please enter a regular expression as you would in Python."
    } else if(this.state.condition === "RuleCondition.if_record_count_above") {
      label = "Count";
      value = this.state.conditional.count;
      onChange = this.handleConditionalChange.bind(this, "count");
      placeholder = "Please enter a number."
    }

    return (
      <ResourceForm data={this.state} baseResource={this.props.baseResource}>
        <SingleFieldElement
            label="Name"
            value={this.state.name}
            controlId="name"
            onChange={this.handleNameChange.bind(this)}
            placeholder="Enter a name for your rule"
        />

        <FormGroup controlId="condition">
          <ControlLabel>Condition</ControlLabel>
          <FormControl componentClass="select" value={this.state.condition} onChange={this.handleTypeChange.bind(this)}>
            <option value="RuleCondition.if_col_present">If Column Present</option>
            <option value="RuleCondition.if_col_not_present">If Column Not Present</option>
            <option value="RuleCondition.if_table_name_matches">If Table Name Matches</option>
            <option value="RuleCondition.if_table_name_does_not_match">If Table Name Does Not Match</option>
            <option value="RuleCondition.if_record_count_above">If Record Count Above</option>
          </FormControl>
        </FormGroup>

        <SingleFieldElement
          label={label}
          value={value}
          controlId={controlId}
          onChange={onChange}
          placeholder={placeholder}
          />

        <HasManyAssociationFormElement
          baseResource="checks"
          label="Checks To Run If This Rule Is True"
          onNewList={this.handleAssocChange.bind(this, "checks")}
          currentList={this.state.checks}
          ListElement={ChecksList} />

        <HasManyAssociationFormElement
          baseResource="rules"
          label="Further Rules To Run If This Rule Is True"
          onNewList={this.handleAssocChange.bind(this, "children")}
          currentList={this.state.children}
          ListElement={RulesList}
          excludedRowIds={[this.state.id]} />
      </ResourceForm>
    )
  }
}

RuleForm.propTypes = {
  data: React.PropTypes.shape({
    id: React.PropTypes.oneOfType([React.PropTypes.number, React.PropTypes.string]).isRequired,
    name: React.PropTypes.string.isRequired,
    condition: React.PropTypes.string.isRequired,
    conditional: React.PropTypes.object.isRequired,
    checks: React.PropTypes.arrayOf(React.PropTypes.shape({
      id: React.PropTypes.oneOfType([React.PropTypes.number, React.PropTypes.string]),
      check_type: React.PropTypes.string.isRequired,
      check_metadata: React.PropTypes.object.isRequired
    })).isRequired,
    children: React.PropTypes.arrayOf(React.PropTypes.shape({
      id: React.PropTypes.oneOfType([React.PropTypes.number, React.PropTypes.string]),
      condition: React.PropTypes.string.isRequired,
      conditional: React.PropTypes.object.isRequired,
    })).isRequired
   })
}

function RuleFormWithData({params}) {
  return (
    <WithData baseResource={"rules/" + params.id}>
      <RuleForm />
    </WithData>

  )
}
export { RuleFormWithData };
