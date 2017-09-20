import React from 'react';
import { PropTypes } from 'prop-types';

import HighchartBase, { connect } from './../HighchartBase';

const highStockConfig = {
  chart: {
    type: 'line',
  },
  xAxis: {},
  yAxis: {},
  plotOptions: {},
};

class HighStock extends HighchartBase {
  constructor(props, context) {
    super(props, context);
  }

  isHighstock() {
    return true;
  }
}

export default connect(HighStock);
