import React, { Component } from 'react';
import logo from './logo.svg';
import './App.css';
import { Button, Table, ControlLabel, FormControl, FormGroup, HelpBlock } from 'react-bootstrap';
import { WithData, List, ResourceForm } from './General';

// General container for all Rules routes. Dont put anything here.
export function Rules(props) {
  return (
    <div>
      {props.children}
    </div>
  )
}

function RulesList(props) {
  let columns = ["id", "condition", "conditional"];
  let columnNames = ["ID", "Rule Condition", "Rule Conditional"];

  return (
    <List columnNames={columnNames} columns={columns} {...props}/>
  );
}

RulesList.propTypes = {
  data: React.PropTypes.arrayOf(React.PropTypes.shape({
     id: React.PropTypes.number.isRequired,
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

  getValidationStateForColumn() {
    const length = this.state.check_metadata.column.length;
    if (length >= 1) return 'success';
    else if (length > 0) return 'error';
  }

  handleChange(e) {
    this.setState({ check_metadata: { column: e.target.value } });
  }

  handleTypeChange(e) {
    this.setState({ rule_type: e.target.value });
  }

  render() {

    let conditionalResource = (<FormGroup
          controlId="columnType"
          validationState={this.getValidationStateForColumn()}
        >
          <ControlLabel>Column</ControlLabel>
          <FormControl
            type="text"
            value={this.state.conditional.column}
            placeholder="Enter text"
            onChange={this.handleConditionalChange.bind(this, "column")}
          />
          <FormControl.Feedback />
        </FormGroup>);

    if(this.state.ruleType.match("table_name")) {
      conditionalResource = (
          <FormGroup controlId="pattern">
          <ControlLabel>Pattern</ControlLabel>
          <FormControl
            type="text"
            value={this.state.conditional.pattern}
            placeholder="Enter a regular expression"
            onChange={this.handleConditionalChange.bind(this, "pattern")}
            help="Any regular expression will do, such as .* or ^customers_\d+$. Exact matches can be done via: ^exact_match_name$."
          />
          <FormControl.Feedback />
        </FormGroup>)
    } else if(this.state.ruleType == "RuleCondition.if_record_count_above") {
      conditionalResource = (
          <FormGroup controlId="pattern">
          <ControlLabel>Count</ControlLabel>
          <FormControl
            type="text"
            value={this.state.conditional.count}
            placeholder="Enter a record count"
            onChange={this.handleConditionalChange.bind(this, "pattern")}
            help="Above this count, the rule will be satisfied and will run it's checks."
          />
          <FormControl.Feedback />
        </FormGroup>)
    }

    return (
      <ResourceForm data={this.state} baseResource={this.props.baseResource}>
        <FormGroup controlId="ruleType">
          <ControlLabel>Rule Type</ControlLabel>
          <FormControl componentClass="select" value={this.state.rule_type} onChange={this.handleTypeChange.bind(this)}>
            <option value="RuleCondition.if_col_present">If Column Present</option>
            <option value="RuleCondition.if_col_not_present">If Column Not Present</option>
            <option value="RuleCondition.if_table_name_matches">If Table Name Matches</option>
            <option value="RuleCondition.if_table_name_does_not_match">If Table Name Does Not Match</option>
            <option value="RuleCondition.if_record_count_above">If Record Count Above</option>
          </FormControl>
        </FormGroup>

        {conditionalResource}
      </ResourceForm>
    )
  }
}

RuleForm.propTypes = {
  data: React.PropTypes.shape({
     id: React.PropTypes.oneOfType([React.PropTypes.number, React.PropTypes.string]).isRequired,
     condition: React.PropTypes.string.isRequired,
     conditional: React.PropTypes.object.isRequired
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


