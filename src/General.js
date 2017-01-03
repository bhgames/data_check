import React, { Component } from 'react';
import { LinkContainer } from 'react-router-bootstrap';
import { Button, Table, ControlLabel, FormGroup, FormControl } from 'react-bootstrap';
import { withRouter } from 'react-router';
import './App.css';
import Config from './Config.js';
import Linkify from 'react-linkify';

/*
   General File contains a lot of the elements used to do the various REST functions
   for each of the resources. Then each Resource's file.js customizes these elements to display
   what they desire for that element.
 */

// capitalize a given string
const capitalize = (string) => string && (string[0].toUpperCase() + string.slice(1))
// convert a snake case string into a nice title
// e.g. snake_case -> Snake Case
const humanize   = (string) => string && string.split('_').map(capitalize).join(' ')

// DATA AND CONTROL ELEMENTS
export class WithData extends Component {

  constructor(props) {
    super(props);
    this.onServerDataChanged();
  }

  onServerDataChanged() {
    let headers = new Headers();
    headers.append('Content-Type', 'application/json');

    let params = { method: 'GET',
                   headers: headers,
                   mode: 'cors'
                 };

    let get = new Request('http://' + Config().apiUrl + '/' + this.props.baseResource);
    let that = this;

    fetch(get, params).then(function(response) {
      return response.json();
    }).then(function(json) {
      that.setState({ data: json })
    })
  }

  deleteDataItem(id) {
    let headers = new Headers();
    headers.append('Content-Type', 'application/json');

    let params = { method: 'DELETE',
                   headers: headers,
                   mode: 'cors'
                 };

    let del = new Request('http://' + Config().apiUrl + '/' + this.props.baseResource + '/' + id);

    let that = this;
    fetch(del, params).then(function(response) {
      that.onServerDataChanged();
    })
  }

  render() {
    if (this.state) {
      const childrenWithProps = React.Children.map(this.props.children,
        (child) => React.cloneElement(child, {
          data: this.state.data,
          baseResource: this.props.baseResource,
          deleteDataItem: this.deleteDataItem.bind(this)
        })
      );

      return <div>{childrenWithProps}</div>
    }

    return <div>Loading...</div>
  }
}

WithData.propTypes = {
  baseResource: React.PropTypes.string.isRequired
}


/* LIST AND DISPLAY ELEMENTS */

/*
  The List class expects to be handed a list of column names and actual columns to call on the data,
  which is expected to be an array.

  An onSelectHandler will be called(if given) whenever a row is clicked.

  SelectedRows is expected to be (if given) an array of objects that have been selected - passing this ensures
  that rows in the data array that are selected are highlighted.

  baseResource is used to assemble links for default buttons, and deleteDataItem is the callback used by the delete button.

  excludedRowIds, if passed, will be used to hide rows in the data array from view.

  buttonMask will hide the Edit, Delete button, New Button depending on values.
  [1,1,1] - Hide all, [1,0,0] - Edit Hidden, Delete & New Not.
  0th index = Edit
  1st index = Delete
  2nd index = New

  children is expected to be <Button> elements you wish to include in Actions in addition to Edit/Delete, with onClick handlers
  bound with the proper this but not yet bound with a proper row(binding will happen here.)

  Please see beneath this function for PropTypes to see proper data typing constraints of each argument.
*/
export class List extends Component {

  constructor(props) {
    super(props);
    this.state = {data: this.props.data, currentSortColumn: 'id', currentSortOrder: 'desc' };
  }

  componentWillReceiveProps(nextProps) {
    this.setState({ data: nextProps.data });
  }


  deleteHandler(row) { if(this.props.deleteDataItem) { this.props.deleteDataItem(row.id) } }

  selectHandler(row) {
    if(this.props.onSelectHandler) {
      this.props.onSelectHandler(row);
    }
  }

  selectedStyleHandler(row) {
    if(this.props.selectedRows && this.props.selectedRows.find((r) => { return r.id === row.id })) {
      return "selected";
    }
  }
  
  buttons(row) {
    let boundButtons = React.Children.map(this.props.children,
        (child) => React.cloneElement(child, {
          onClick: child.props.onClick.bind(null, row)
        })
      );

    let defaultButtons = [];

    if(this.props.buttonMask[0] === 0) {
      defaultButtons.push(
        <LinkContainer to={'/' + this.props.baseResource + '/' + row.id + '/edit'} key={'edit'}>
          <Button>Edit</Button>
        </LinkContainer>
      )
    }

    if(this.props.buttonMask[1] === 0) {
      defaultButtons.push(<Button onClick={this.deleteHandler.bind(this, row)} key={'delete'}>Delete</Button>)
    }

    return <td>
      {defaultButtons}
      {boundButtons}
    </td>
  }

  changeSort(colName) {
    let col = this.props.columns[this.props.columnNames.indexOf(colName)];
    let sort = this.state.currentSortOrder;
    if (col == this.state.currentSortColumn) {
      sort = sort == "asc" ? "desc" : "asc";
    }

    this.setState({ currentSortColumn: col, currentSortOrder: sort}); 
  }

  render() {

    let rowIds = this.props.data.map((r) => { return r.id });
    let displayedRows = this.props.data.filter((r) => { return !this.props.excludedRowIds || !this.props.excludedRowIds.includes(rowIds[this.props.data.indexOf(r)])});
    
    let currentSO = this.state.currentSortOrder;
    let currentSC = this.state.currentSortColumn;

    displayedRows = displayedRows.sort((a,b) => {
      if(currentSO === 'desc') {
        return a[currentSC] > b[currentSC]
      } else {
        return a[currentSC] < b[currentSC]
      }
    });

    let buttonHeader = <th>Actions</th>;

    let newButton = this.props.buttonMask[2] === 1 ? null : <LinkContainer to={ this.props.baseResource + '/new/edit'}>
          <Button bsStyle="primary">New</Button>
        </LinkContainer>;


    return (
      <div>
        <h2>{humanize(this.props.baseResource)} {newButton}</h2>
        <Table responsive striped bordered condensed hover>
          <thead>
            <tr>
              {this.props.columnNames.map(name =>
                <th key={name} onClick={this.changeSort.bind(this, name)}>{name}</th>
              )}
              {buttonHeader}
            </tr>
          </thead>
          <tbody>
            {displayedRows.map(row =>
              <tr key={displayedRows.indexOf(row)} onClick={this.selectHandler.bind(this, row)} className={this.selectedStyleHandler(row)}>
                {this.props.columns.map(col =>
                  <td key={col}><Linkify>{typeof row[col] === 'object' ? JSON.stringify(row[col]) : row[col]}</Linkify></td>
                )}
                {this.buttons(row)}
              </tr>
            )}
          </tbody>
        </Table>
      </div>
    );
  }
}

List.propTypes = {
  data: React.PropTypes.arrayOf(React.PropTypes.object).isRequired,
  columnNames: React.PropTypes.arrayOf(React.PropTypes.string).isRequired,
  columns: React.PropTypes.arrayOf(React.PropTypes.string).isRequired,
  baseResource: React.PropTypes.string.isRequired,
  deleteDataItem: React.PropTypes.func.isRequired,
  onSelectHandler: React.PropTypes.func,
  selectedRows: React.PropTypes.array,
  excludedRowIds: React.PropTypes.array, // Used to prevent cyclical Rule depedencies, or similar.
  buttonMask: React.PropTypes.arrayOf(React.PropTypes.number).isRequired // Used to hide edit/delete buttons. See comments above.
};

List.defaultProps = {
  buttonMask: [0,0,0] // Show all edit delete new by default.
}


/* FORM ELEMENTS */


export function HasManyAssociationFormElement({ label, baseResource, onNewList, currentList, ListElement, excludedRowIds }) {
  let handleArrChange = (obj) => {
    let found = currentList.find((c) => { return c.id === obj.id });

    if(found) {
      currentList.splice(currentList.indexOf(found), 1);
    } else {
      currentList.push(obj);
    }

    onNewList(currentList);
  }

  return (
      <FormGroup controlId={baseResource}>
        <ControlLabel>{label}</ControlLabel>
        <WithData baseResource={baseResource}>
          <ListElement onSelectHandler={handleArrChange.bind(this)} selectedRows={currentList} buttonMask={[1,1,1]} excludedRowIds={excludedRowIds}/>
        </WithData>
      </FormGroup>
    );
}

HasManyAssociationFormElement.propTypes = {
  label: React.PropTypes.string.isRequired,
  baseResource: React.PropTypes.string.isRequired,
  onNewList: React.PropTypes.func.isRequired,
  currentList: React.PropTypes.array.isRequired,
  ListElement: React.PropTypes.func.isRequired,
  excludedRowIds: React.PropTypes.array
}

HasManyAssociationFormElement.defaultProps = {
  excludedRowIds: []
}

export function SingleFieldElement({ controlId, label, value, type, placeholder, onChange}) {
   return (<FormGroup
          controlId={controlId}
        >
          <ControlLabel>{label}</ControlLabel>
          <FormControl
            type={type}
            value={value}
            placeholder={placeholder}
            onChange={onChange}
          />
          <FormControl.Feedback />
        </FormGroup>);
}

SingleFieldElement.propTypes = {
  controlId: React.PropTypes.string,
  label: React.PropTypes.string.isRequired,
  value: React.PropTypes.oneOfType([React.PropTypes.string, React.PropTypes.number]),
  type: React.PropTypes.oneOf(["text"]),
  placeholder: React.PropTypes.string,
  onChange: React.PropTypes.func.isRequired
}

SingleFieldElement.defaultProps = {
  type: "text"
}

function UnwrappedResourceForm({router, data, baseResource, children}) {

  let submit = function(e) {
    e.preventDefault();
    let headers = new Headers();
    headers.append('Content-Type', 'application/json');

    let params = { method: 'PUT',
                   headers: headers,
                   mode: 'cors',
                   body: JSON.stringify(data)
                 };

    let add = baseResource;

    if(data.id === "new") {
      add = baseResource.split("/new")[0];
      params.method = 'POST';
    }

    let post = new Request('http://' + Config().apiUrl + '/' + add);

    fetch(post,params).then(function(response) {
      if(response.ok) {
        router.goBack();
        //router.push('/' + baseResource.split("/")[0]);
      } else {
        console.log(response);
      }
    })

  }

  return (
    <form onSubmit={submit}>
      {children}
      <Button type="submit">
        Submit
      </Button>
    </form>
  )

}

UnwrappedResourceForm.propTypes = {
  data: React.PropTypes.shape({
    id: React.PropTypes.oneOfType([React.PropTypes.number, React.PropTypes.string]).isRequired
  }).isRequired,
  baseResource: React.PropTypes.string.isRequired
}

let ResourceForm = withRouter(UnwrappedResourceForm);
export { ResourceForm };
