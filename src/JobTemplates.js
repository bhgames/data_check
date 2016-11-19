import React, { Component } from 'react';
import './App.css';
import { ControlLabel, FormControl, FormGroup } from 'react-bootstrap';
import { RulesList } from './Rules';
import { WithData, List, ResourceForm, HasManyAssociationFormElement, SingleFieldElement } from './General';

// General container for all JobTemplates routes. Dont put anything here.
export function JobTemplates(props) {
  return (
    <div>
      {props.children}
    </div>
  )
}

function JobTemplatesList(props) {
  let columns = ["id", "name", "parallelization"];
  let columnNames = ["ID", "Name", "Parallelization"];

  return (
    <List columnNames={columnNames} columns={columns} {...props}/>
  );
}

JobTemplatesList.propTypes = {
  data: React.PropTypes.arrayOf(React.PropTypes.shape({
     id: React.PropTypes.number.isRequired,
     name: React.PropTypes.string.isRequired,
     parallelization: React.PropTypes.number.isRequired
   })).isRequired
}

JobTemplatesList.defaultProps = {
  data: []
};


export function JobTemplatesListWithData() {
  return (
    <WithData baseResource="job_templates">
      <JobTemplatesList />
    </WithData>
  )
}


class JobTemplateForm extends Component {

  constructor(props) {
    super(props);
    this.state = props.data;
  }

  componentWillReceiveProps(nextProps) {
    this.setState(nextProps.data);
  }

  handleChange(type, e) {
    let newState = { };
    newState[type] = e.target.value;
    this.setState(newState);
  }

  handleAssocChange(stateKey, newList) {
    let newState = {};
    newState[stateKey] = newList;
    this.setState(newState);
  }

  render() {

    return (
      <ResourceForm data={this.state} baseResource={this.props.baseResource}>
        
        <SingleFieldElement 
          label="Name"
          value={this.state.name}
          controlId="Name"
          onChange={this.handleChange.bind(this, "name")}
          placeholder={"Enter Template Name"}
          />

        <SingleFieldElement 
          label="Parallelization"
          value={this.state.parallelization}
          controlId="Parallelization"
          onChange={this.handleChange.bind(this, "parallelization")}
          placeholder={"Enter Number of Threads to Use"}
          />

        <HasManyAssociationFormElement 
          baseResource="rules" 
          label="Rules to Run"
          onNewList={this.handleAssocChange.bind(this, "rules")}
          currentList={this.state.rules}
          ListElement={RulesList} />
      </ResourceForm>
    )
  }
}

JobTemplateForm.propTypes = {
  data: React.PropTypes.shape({
    id: React.PropTypes.oneOfType([React.PropTypes.number, React.PropTypes.string]).isRequired,
    name: React.PropTypes.string.isRequired,
    parallelization: React.PropTypes.number.isRequired,
    rules: React.PropTypes.arrayOf(React.PropTypes.shape({
      id: React.PropTypes.oneOfType([React.PropTypes.number, React.PropTypes.string]),
      condition: React.PropTypes.string.isRequired,
      conditional: React.PropTypes.object.isRequired
    })).isRequired
   })
}

function JobTemplateFormWithData({params}) {
  return (
    <WithData baseResource={"job_templates/" + params.id}>
      <JobTemplateForm />
    </WithData>

  )
}
export { JobTemplateFormWithData };


