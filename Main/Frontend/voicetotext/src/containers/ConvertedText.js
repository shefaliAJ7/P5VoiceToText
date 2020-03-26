import React, { Component } from './../../node_modules/react';
import { Button } from 'react-bootstrap';
import './../../node_modules/ag-grid-community/dist/styles/ag-grid.css';
import './../../node_modules/ag-grid-community/dist/styles/ag-theme-balham.css';
import './../styles/index.css';

class ConvertedText extends Component {
  constructor(props) {
    super(props);
  }

  render() {
    if (!this.props.loading) {
      return null;
    } else {
      return (
        <div>
          <form onSubmit={this.props.handleSubmit}>
            <div className='Textareasize'>
              <textarea
                className='form-control'
                id='Textarea'
                value={this.props.title}
                onChange={this.props.handleChange}
                required
              />
            </div>

            <Button className='Save' type='submit'>
              Save
            </Button>
          </form>
        </div>
      );
    }
  }
}

export default ConvertedText;
