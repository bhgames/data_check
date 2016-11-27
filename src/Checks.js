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

  handleChange(e) {
    this.setState({ check_metadata: { column: e.target.value } });
  }

  handleTypeChange(e) {
    this.setState({ check_type: e.target.value });
  }

  render() {

    return (
      <ResourceForm data={this.state} baseResource={this.props.baseResource}>
        <FormGroup controlId="checkType">
          <ControlLabel>Check Type</ControlLabel>
          <FormControl componentClass="select" value={this.state.check_type} onChange={this.handleTypeChange.bind(this)}>
            <option value="CheckType.uniqueness">Uniqueness</option>
            <option value="CheckType.null">Null</option>
            <option value="CheckType.date_gap">DateGap</option>
          </FormControl>
        </FormGroup>

        <SingleFieldElement
          value={this.state.check_metadata.column}
          placeholder="Enter text"
          onChange={this.handleChange.bind(this)}
          label="Column to Check"
          controlId="columnType"
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


