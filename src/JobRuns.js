import React, { Component } from 'react';
import './App.css';
import { ControlLabel, FormControl, FormGroup } from 'react-bootstrap';
import { ChecksList } from './Checks';
import { WithData, List, ResourceForm, HasManyAssociationFormElement, SingleFieldElement } from './General';

// General container for all JobRuns routes. Dont put anything here.
export function JobRuns(props) {
  return (
    <div>
      {props.children}
    </div>
  )
}

export function JobRunsList(props) {
  let columns = ["id", "job_template_name", "scheduled_at", "rejected_at", "failed_at", "cancelled_at", "run_at", "finished_at", "status"];
  let columnNames = ["ID", "Template Name", "Scheduled At", "Rejected At", "Failed At", "Cancelled At", "Run At", "Finished At", "Status"];

  return (
    <List columnNames={columnNames} columns={columns} buttonMask={[1,0,1]} {...props}/>
  );
}

JobRunsList.propTypes = {
  data: React.PropTypes.arrayOf(React.PropTypes.shape({
      id: React.PropTypes.number.isRequired,
      job_template_name: React.PropTypes.string.isRequired,
      scheduled_at: React.PropTypes.string.isRequired,
      failed_at: React.PropTypes.string.isRequired,
      cancelled_at: React.PropTypes.string.isRequired,
      run_at: React.PropTypes.string.isRequired,
      finished_at: React.PropTypes.string.isRequired,
      status: React.PropTypes.string.isRequired
   })).isRequired
}

JobRunsList.defaultProps = {
  data: []
};


export function JobRunsListWithData() {
  return (
    <WithData baseResource="job_runs">
      <JobRunsList />
    </WithData>
  )
}


