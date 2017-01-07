import React, { Component } from 'react';
import './App.css';
import { Button, Checkbox } from 'react-bootstrap';
import { RulesList } from './Rules';
import { DataSourcesList } from './DataSources';
import { WithData, List, ResourceForm, HasManyAssociationFormElement, SingleFieldElement } from './General';
import Config from './Config.js';

// General container for all JobTemplates routes. Dont put anything here.
export function JobTemplates(props) {
  return (
    <div>
      {props.children}
    </div>
  )
}

export function JobTemplatesList(props) {
  let columns = ["id", "name", "parallelization"];
  let columnNames = ["ID", "Name", "Parallelization"];

  let run = (row) => {
    let headers = new Headers();
    headers.append('Content-Type', 'application/json');

    let params = { method: 'POST',
                   headers: headers,
                   mode: 'cors',
                   body: JSON.stringify({ job_template_id: row.id })
                 };
    
    let post = new Request('http://' + Config().apiUrl + '/job_runs');

    fetch(post, params).then(function(response) {
      return response.json();
    }).then(function(json) {
      alert("Job Run Started. Replace me with a real noty.");
    })

  };

  return (
    <List columnNames={columnNames} columns={columns} {...props}>
        <Button onClick={run.bind(this)}>Run</Button>
    </List>
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

  handleMetadataCheckboxToggle(type) {
    let newState = { };
    newState[type] = !this.state[type];
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
          controlId="name"
          onChange={this.handleChange.bind(this, "name")}
          placeholder={"Enter Template Name"}
          />

        <SingleFieldElement 
          label="Parallelization"
          value={this.state.parallelization}
          controlId="parallelization"
          onChange={this.handleChange.bind(this, "parallelization")}
          placeholder={"Enter Number of Threads to Use"}
          />

        <Checkbox 
          checked={this.state.ignore_system_failures} 
          label="Ignore any system-related exception thrown by checks?" 
          onChange={this.handleMetadataCheckboxToggle.bind(this, "ignore_system_failures")}>
        Ignore System Failures </Checkbox>

        <HasManyAssociationFormElement 
          baseResource="rules" 
          label="Rules to Run"
          onNewList={this.handleAssocChange.bind(this, "rules")}
          currentList={this.state.rules}
          ListElement={RulesList} />

      <HasManyAssociationFormElement 
          baseResource="data_sources" 
          label="Data Sources"
          onNewList={this.handleAssocChange.bind(this, "data_sources")}
          currentList={this.state.data_sources}
          ListElement={DataSourcesList} />
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
    })).isRequired,
    data_sources: React.PropTypes.arrayOf(React.PropTypes.shape({
      id: React.PropTypes.oneOfType([React.PropTypes.number, React.PropTypes.string]),
      data_source_type: React.PropTypes.string.isRequired,
      host: React.PropTypes.string.isRequired,
      schemas: React.PropTypes.arrayOf(React.PropTypes.string).isRequired
    })).isRequired,
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


