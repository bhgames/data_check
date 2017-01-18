import React, { Component } from 'react';
import './App.css';
import { ControlLabel, FormControl, FormGroup } from 'react-bootstrap';
import { WithData, List, ResourceForm, SingleFieldElement } from './General';

// General container for all DataSources routes. Dont put anything here.
export function DataSources(props) {
  return (
    <div>
      {props.children}
    </div>
  )
}

export function DataSourcesList(props) {
  let columns = ["id", "data_source_type", "host", "schemas"];
  let columnNames = ["ID", "Type", "Host", "Schemas"];

  return (
    <List columnNames={columnNames} columns={columns} {...props}/>
  );
}

DataSourcesList.propTypes = {
  data: React.PropTypes.arrayOf(React.PropTypes.shape({
     id: React.PropTypes.number.isRequired,
     data_source_type: React.PropTypes.string.isRequired,
     host: React.PropTypes.string.isRequired,
     schemas: React.PropTypes.arrayOf(React.PropTypes.string).isRequired
   })).isRequired
}

DataSourcesList.defaultProps = {
  data: []
};


export function DataSourcesListWithData() {
  return (
    <WithData baseResource="data_sources">
      <DataSourcesList />
    </WithData>
  )
}


class DataSourceForm extends Component {

  constructor(props) {
    super(props);
    props.data.schemasAsString = props.data.schemas.join(",");
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

  handleSchemaChange(e) {
    this.setState({schemas: e.target.value.split(","), schemasAsString: e.target.value})
  }

  render() {

    return (
      <ResourceForm data={this.state} baseResource={this.props.baseResource}>
        <FormGroup controlId="dataSourceType">
          <ControlLabel>Data Source Type</ControlLabel>
          <FormControl componentClass="select" value={this.state.data_source_type} onChange={this.handleChange.bind(this, "data_source_type")}>
            <option value="DataSourceType.impala">Impala</option>
            <option value="DataSourceType.postgres">Postgres</option>
          </FormControl>
        </FormGroup>

        <SingleFieldElement 
          label="Host"
          value={this.state.name}
          controlId="host"
          onChange={this.handleChange.bind(this, "host")}
          placeholder={"Enter Host"}
          />

        <SingleFieldElement 
          label="Port"
          value={this.state.port}
          controlId="port"
          onChange={this.handleChange.bind(this, "port")}
          placeholder={"Enter Port"}
          />

        <SingleFieldElement 
          label="User"
          value={this.state.user}
          controlId="user"
          onChange={this.handleChange.bind(this, "user")}
          placeholder={"Enter Username"}
          />

        <SingleFieldElement 
          label="Password"
          value={this.state.password}
          controlId="password"
          onChange={this.handleChange.bind(this, "password")}
          placeholder={"Enter Password"}
          />


        <SingleFieldElement 
          label="DBName"
          value={this.state.dbname}
          controlId="dbname"
          onChange={this.handleChange.bind(this, "dbname")}
          placeholder={"Enter DBName(If relevant)"}
          />


        <SingleFieldElement 
          label="Schemas"
          value={this.state.schemasAsString}
          controlId="schemas"
          onChange={this.handleSchemaChange.bind(this)}
          placeholder={"Enter Schema List (Comma Separated)"}
          />

      </ResourceForm>
    )
  }
}

DataSourceForm.propTypes = {
  data: React.PropTypes.shape({
    id: React.PropTypes.oneOfType([React.PropTypes.number, React.PropTypes.string]).isRequired,
    host: React.PropTypes.string.isRequired,
    port: React.PropTypes.number.isRequired,
    user: React.PropTypes.string.isRequired,
    password: React.PropTypes.string.isRequired,
    data_source_type: React.PropTypes.oneOf(["DataSourceType.impala"]).isRequired,
    schemas: React.PropTypes.arrayOf(React.PropTypes.string).isRequired
   })
}

function DataSourceFormWithData({params}) {
  return (
    <WithData baseResource={"data_sources/" + params.id}>
      <DataSourceForm />
    </WithData>

  )
}
export { DataSourceFormWithData };


