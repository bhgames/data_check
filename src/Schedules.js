import React, { Component } from 'react';
import './App.css';
import { Checkbox } from 'react-bootstrap';
import { WithData, List, ResourceForm, HasManyAssociationFormElement, SingleFieldElement } from './General';
import { JobTemplatesList } from './JobTemplates';

// General container for all Schedules routes. Dont put anything here.
export function Schedules(props) {
  return (
    <div>
      {props.children}
    </div>
  )
}

export function SchedulesList(props) {
  let columns = ["id", "schedule_config", "job_templates_names"];
  let columnNames = ["ID", "Schedule Config", "Job Templates"];

  return (
    <List columnNames={columnNames} columns={columns} {...props}/>
  );
}

SchedulesList.propTypes = {
  data: React.PropTypes.arrayOf(React.PropTypes.shape({
      id: React.PropTypes.number.isRequired,
      schedule_config: React.PropTypes.object.isRequired,
      job_templates: React.PropTypes.arrayOf(React.PropTypes.shape({
        id: React.PropTypes.number.isRequired,
        name: React.PropTypes.string.isRequired,
        parallelization: React.PropTypes.number.isRequired
      })).isRequired,
      job_templates_names: React.PropTypes.string.isRequired, 
      active: React.PropTypes.bool.isRequired
   })).isRequired
}

SchedulesList.defaultProps = {
  data: []
};


export function SchedulesListWithData() {
  return (
    <WithData baseResource="schedules">
      <SchedulesList />
    </WithData>
  )
}


class ScheduleForm extends Component {

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

  handleScheduleConfigChange(type, e) {
    let conf = this.state.schedule_config;
    conf[type] = e.target.value;
    this.setState({schedule_config: conf});
  }

  render() {

    return (
      <ResourceForm data={this.state} baseResource={this.props.baseResource}>
        <p>Values are meant to be in cron syntax, eg. 3 or */10 or 3,5. Day_of_week can be thu,fri for example.</p><br />

        {[["Minute", "minute"], ["Hour", "hour"], ["Day of Week", "day_of_week"]].map((val) => 
          <SingleFieldElement 
            key={val[0]}
            label={val[0]}
            value={this.state.schedule_config[val[1]]}
            controlId={val[1]}
            onChange={this.handleScheduleConfigChange.bind(this, val[1])}
            placeholder={"Enter " + val[0]}
            />
          )
        }

        <Checkbox 
          value={this.state.active} 
          label="Active" 
          onChange={this.handleChange.bind(this, "active")}
        > Active </Checkbox>

        <HasManyAssociationFormElement 
            baseResource="job_templates" 
            label="Job Templates"
            onNewList={this.handleAssocChange.bind(this, "job_templates")}
            currentList={this.state.job_templates}
            ListElement={JobTemplatesList} />
      </ResourceForm>
    )
  }
}

ScheduleForm.propTypes = {
  data: React.PropTypes.shape({
    id: React.PropTypes.oneOfType([React.PropTypes.string, React.PropTypes.number]).isRequired,
    schedule_config: React.PropTypes.object.isRequired,
    job_templates: React.PropTypes.arrayOf(React.PropTypes.shape({
      id: React.PropTypes.number.isRequired,
      name: React.PropTypes.string.isRequired,
      parallelization: React.PropTypes.number.isRequired
    })).isRequired,
    active: React.PropTypes.bool.isRequired
  })
}

function ScheduleFormWithData({params}) {
  return (
    <WithData baseResource={"schedules/" + params.id}>
      <ScheduleForm />
    </WithData>

  )
}
export { ScheduleFormWithData };


