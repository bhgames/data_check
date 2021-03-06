import React, { Component } from 'react';
import './App.css';
import { Grid, Row, Col, Button, PageHeader, Accordion, Panel } from 'react-bootstrap';
import { WithData, List } from './General';
import { withRouter } from 'react-router';
import { Pie } from 'react-chartjs';

// General container for all JobRuns routes. Dont put anything here.
export function JobRuns(props) {
  return (
    <div>
      {props.children}
    </div>
  )
}

function UnwrappedJobRunsList(props) {
  let columns = ["id", "job_template_name", "scheduled_at", "rejected_at", "failed_at", "cancelled_at", "run_at", "finished_at", "status"];
  let columnNames = ["ID", "Template Name", "Scheduled At", "Rejected At", "Failed At", "Cancelled At", "Run At", "Finished At", "Status"];

  let goto = (row) => {
    props.router.push('/job_runs/' + row.id);
  }

  return (
    <List columnNames={columnNames} columns={columns} buttonMask={[1,0,1]} {...props}>
      <Button onClick={goto.bind(this)}>View</Button>
    </List>
  );
}

UnwrappedJobRunsList.propTypes = {
  data: React.PropTypes.arrayOf(React.PropTypes.shape({
      id: React.PropTypes.number.isRequired,
      job_template_name: React.PropTypes.string.isRequired,
      scheduled_at: React.PropTypes.string.isRequired,
      failed_at: React.PropTypes.string,
      cancelled_at: React.PropTypes.string,
      run_at: React.PropTypes.string,
      finished_at: React.PropTypes.string,
      status: React.PropTypes.string.isRequired
   })).isRequired
}

UnwrappedJobRunsList.defaultProps = {
  data: []
};

let JobRunsList = withRouter(UnwrappedJobRunsList);

export function JobRunsListWithData() {
  return (
    <WithData baseResource="job_runs">
      <JobRunsList />
    </WithData>
  )
}


function SuccessFailTablePieChart({ totalFail, totalSuccess, totalException, labelSuccess, labelFail, labelException }) {
  let data = [{label: labelFail, color: '#F7464A', highlight: '#FF5A5E', value: totalFail}, 
              {label: labelSuccess, color: '#46BFBD', highlight: '#5AD3D1', value: totalSuccess},
              {label: labelException, color: '#D3D3D3', highlight: '#D3D3D3', value: totalException}]
  return <Pie data={data}/>
}

SuccessFailTablePieChart.propTypes = {
  totalFail: React.PropTypes.number.isRequired,
  totalSuccess: React.PropTypes.number.isRequired,
  totalException: React.PropTypes.number.isRequired
}

function ByTypeTablePieChart({ types }) {
  let data = [];

  for(let t of Object.keys(types)) {
    data.push({label: t, value: types[t]}); 
  }

  return <Pie data={data}/>
}

ByTypeTablePieChart.propTypes = {
  types: React.PropTypes.object.isRequired
}


class JobRunsView extends Component {
  getAllChecks(rule) {
    let start = [].concat(rule.checks);
    for(let r of rule.children) {
      start = start.concat(this.getAllChecks(r));
    }
    return start;
  }

  tableString(metadata) {
    return metadata.table + "|" + metadata.source_id + "|" + metadata.schema;
  }

  render() {

    let jr = this.props.data;
    let jt = jr.job_template;
    let tsColumns = ["scheduled_at", "rejected_at", "failed_at", "cancelled_at", "run_at", "finished_at"];
    let tsColumnNames = ["Scheduled At", "Rejected At", "Failed At", "Cancelled At", "Run At", "Finished At"];
    let noop = (row) => {};

    let logColumns=["event", "message", "time"];
    let logLabels = ["Event", "Message", "Time"];

    // TODO REFACTOR EACH CHECK TO CONTAIN ONE LOG PER "UNIT" WORK INSTEAD OF LUMPING ALL TOGETHER.
    // THIS WILL PREVENT THIS MAD FILTERING FROM HAPPENING BELOW.
    let allChecks = jt.rules.map((r) => this.getAllChecks(r));
    allChecks = allChecks.reduce((list, arrOfChecks) => {
      for(let c of arrOfChecks) {
        let byId = list.map((chk) => chk.id);
        if(byId.indexOf(c.id) === -1) {
       	  list.push(c);
        }
      }

      return list;
    }, []);

    let allCheckLogs = jr.all_connected_logs.filter((l) => l.loggable_type === "check");
    let allExceptions = allCheckLogs.map((l) => l.log).reduce((a, b) => a.concat(b), []).filter((l) => l.metadata.traceback);
    let allExceptionsMetadata = allExceptions.map((l) => l.metadata);
    let allCheckLogsWithCheckObj = allCheckLogs.map((l) => [l, allChecks.find((c) => c.id === l.loggable_id)]);
    let allCheckLogsLogDataWithCheckObj = allCheckLogsWithCheckObj.map((lAndC) => [lAndC[0].log, lAndC[1]]);

    let allFailedCheckEventsWithCheckObj = allCheckLogsWithCheckObj.map((lAndC) => [lAndC[0].log.filter((logEntry) => logEntry.event === "check_failed"), lAndC[1]]);
    let allSucceededCheckEventsWithCheckObj = allCheckLogsWithCheckObj.map((lAndC) => [lAndC[0].log.filter((logEntry) => logEntry.event === "check_succeeded"), lAndC[1]]);
    let allExceptionCheckEventsWithCheckObj = allCheckLogsWithCheckObj.map((lAndC) => [lAndC[0].log.filter((logEntry) => logEntry.event === "failed"), lAndC[1]]);
    let allFailedTablesAndChecks = allFailedCheckEventsWithCheckObj.map((lAndC) => [lAndC[0].map((logEntry) => logEntry.metadata), lAndC[1]]);
    let allSucceededTablesAndChecks = allSucceededCheckEventsWithCheckObj.map((lAndC) => [lAndC[0].map((logEntry) => logEntry.metadata), lAndC[1]]);
    let allExceptionsAndChecks = allExceptionCheckEventsWithCheckObj.map((lAndC) => [lAndC[0].map((logEntry) => logEntry.metadata), lAndC[1]]);

    let failedTables = [];
    let exceptionTables = [];
    let succeededTables = [];
    let byCheckExceptionTables = {};

    let successCheckCount = 0;
    let failedCheckCount = 0;
    let exceptionCheckCount = 0;

    let byTypeFailCount = {};


    allExceptionsAndChecks.map((lAndC) => {
      let tableMetas = lAndC[0];

      if(!byCheckExceptionTables[lAndC[1].id]) {
        byCheckExceptionTables[lAndC[1].id] = [];
      }

      for(let table of tableMetas) {
        if(!exceptionTables.includes(this.tableString(table))) {
          exceptionTables.push(this.tableString(table));
        }

        // Only count a failed table once per check, but it will retry three times, so use this hash.
        if(!byCheckExceptionTables[lAndC[1].id].includes(this.tableString(table))) {
          byCheckExceptionTables[lAndC[1].id].push(this.tableString(table));
          exceptionCheckCount++; 
        }
      }
    });

    let allFailedLogsAndChecks = allFailedTablesAndChecks.map((lAndC) => {
      let tableMetas = lAndC[0];
      let index = allFailedTablesAndChecks.indexOf(lAndC);
      let allLogsFromThisCheck = allCheckLogsWithCheckObj[index][0].log;
      let arrOfFailedLogs = [];

      for(let failedTable of tableMetas) {
        if(!failedTables.includes(this.tableString(failedTable)) && !exceptionTables.includes(this.tableString(failedTable))) {
          failedTables.push(this.tableString(failedTable));
        }

        failedCheckCount++;

        if(byTypeFailCount[lAndC[1].check_type] === undefined) {
          byTypeFailCount[lAndC[1].check_type] = 1;
        } else {
          byTypeFailCount[lAndC[1].check_type] += 1;
        }

        let allTableLogsFromThisCheck = allLogsFromThisCheck.filter((logEntry) => this.tableString(logEntry.metadata) === this.tableString(failedTable));
        arrOfFailedLogs = arrOfFailedLogs.concat(allTableLogsFromThisCheck);
      }
      return [arrOfFailedLogs, lAndC[1]]
    });
    

    allSucceededTablesAndChecks.map((lAndC) => {
      let tableMetas = lAndC[0];

      for(let succeededTable of tableMetas) {
        if(!succeededTables.includes(this.tableString(succeededTable)) && !failedTables.includes(this.tableString(succeededTable)) && !exceptionTables.includes(this.tableString(succeededTable))) {
          succeededTables.push(this.tableString(succeededTable));
        }

        successCheckCount++;
      }
    })

    console.log(allCheckLogsWithCheckObj);
    return (
      <Grid>
        <Row>
          <Col md={6} xs={12}>
            <PageHeader>{jr.job_template_name}</PageHeader>
          </Col>
          <Col md={6} xs={6}>
            <PageHeader><small>{jr.status}</small></PageHeader>
          </Col>
        </Row>

        <Row>
          <Col>
            <List columnNames={tsColumnNames} columns={tsColumns} buttonMask={[1,1,1]} baseResource="job_runs" deleteDataItem={noop} data={[jr]}/>
          </Col>
        </Row>

        <Row>
          <Col md={4} xs={12}>
            <PageHeader><small>Table Stats</small></PageHeader>
            <SuccessFailTablePieChart totalFail={failedTables.length} totalSuccess={succeededTables.length} totalException={exceptionTables.length} labelSuccess="Tables Succeeded" labelFail="Tables Failed" labelException="Tables Errored Out" />
          </Col>
          <Col md={4} xs={12}>
            <PageHeader><small>Check Stats</small></PageHeader>
            <SuccessFailTablePieChart totalFail={failedCheckCount} totalSuccess={successCheckCount} totalException={exceptionCheckCount} labelSuccess="Checks Succeeded" labelFail="Checks Failed" labelException="Checks Errored Out" />
          </Col>
          <Col md={4} xs={12}>
            <PageHeader><small>Failures by Check Type</small></PageHeader>
            <ByTypeTablePieChart types={byTypeFailCount} />
          </Col>
        </Row>

        <Row>
          <Col>
          <PageHeader><small>Failures</small></PageHeader>
            <Accordion>
              {allFailedLogsAndChecks.map(row => 
                <Panel header={row[1].check_type} eventKey={allFailedLogsAndChecks.indexOf(row)} key={allFailedLogsAndChecks.indexOf(row)}>
                  <List columnNames={logLabels} columns={logColumns} buttonMask={[1,1,1]} baseResource="checks" deleteDataItem={noop} data={row[0]} />
                </Panel>
              )}
            </Accordion>
          </Col>
        </Row>

        <Row>
          <Col>
          <PageHeader><small>All Logs</small></PageHeader>
            <Accordion>
              {allCheckLogsLogDataWithCheckObj.map(row => 
                <Panel header={row[1].check_type} eventKey={allCheckLogsLogDataWithCheckObj.indexOf(row)} key={allCheckLogsLogDataWithCheckObj.indexOf(row)}>
                  <List columnNames={logLabels} columns={logColumns} buttonMask={[1,1,1]} baseResource="checks" deleteDataItem={noop} data={row[0]} />
                </Panel>
              )}
            </Accordion>
          </Col>
        </Row>

        <Row>
          <Col>
          <PageHeader><small>All Exceptions</small></PageHeader>
            <Accordion>
              <Panel header='Exceptions'>
                <List columnNames={['Exception']} columns={['traceback']} buttonMask={[1,1,1]} baseResource="exceptions" deleteDataItem={noop} data={allExceptionsMetadata} />
              </Panel>
            </Accordion>
          </Col>
        </Row>
      </Grid>
    )
  }
}

JobRunsView.propTypes = {
  data: React.PropTypes.shape({
      id: React.PropTypes.number.isRequired,
      job_template_name: React.PropTypes.string.isRequired,
      scheduled_at: React.PropTypes.string.isRequired,
      failed_at: React.PropTypes.string,
      cancelled_at: React.PropTypes.string,
      run_at: React.PropTypes.string,
      finished_at: React.PropTypes.string,
      status: React.PropTypes.string.isRequired,
      job_template: React.PropTypes.shape({
        id: React.PropTypes.oneOfType([React.PropTypes.number, React.PropTypes.string]).isRequired,
        name: React.PropTypes.string.isRequired,
        parallelization: React.PropTypes.number.isRequired,
        rules: React.PropTypes.arrayOf(React.PropTypes.shape({
          id: React.PropTypes.oneOfType([React.PropTypes.number, React.PropTypes.string]),
          condition: React.PropTypes.string.isRequired,
          conditional: React.PropTypes.object.isRequired,
          checks: {}
        })).isRequired,
        data_sources: React.PropTypes.arrayOf(React.PropTypes.shape({
          id: React.PropTypes.oneOfType([React.PropTypes.number, React.PropTypes.string]),
          data_source_type: React.PropTypes.string.isRequired,
          host: React.PropTypes.string.isRequired,
          schemas: React.PropTypes.arrayOf(React.PropTypes.string).isRequired
        })).isRequired,
       }),
      all_connected_logs: React.PropTypes.arrayOf(React.PropTypes.shape({
        id: React.PropTypes.number.isRequired,
        loggable_type: React.PropTypes.string.isRequired,
        loggable_id: React.PropTypes.number.isRequired,
        log: React.PropTypes.arrayOf(React.PropTypes.shape({
          time: React.PropTypes.string.isRequired,
          event: React.PropTypes.string.isRequired,
          message: React.PropTypes.string.isRequired,
          metadata: React.PropTypes.object.isRequired
        })).isRequired
      }))
  }).isRequired
}


export function JobRunsViewWithData({params}) {
  return (
    <WithData baseResource={"job_runs/" + params.id}>
      <JobRunsView />
    </WithData>

  )
}
