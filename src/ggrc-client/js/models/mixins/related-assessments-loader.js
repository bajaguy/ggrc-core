/*
    Copyright (C) 2019 Google Inc.
    Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
*/

import Mixin from './mixin';
import {isSnapshot} from '../../plugins/utils/snapshot-utils';

export default Mixin.extend({}, {
  /**
   *
   * @param {Array} limit - Limit of loaded numbers
   * @param {Array} orderBy - Key: property name, Value: sorting direction (asc, desc)
   * @return {Promise}
   */
  getRelatedAssessments(limit = [0, 5], orderBy = []) {
    const type = this.attr('type');
    const instanceId = isSnapshot(this) ?
      this.snapshot.child_id :
      this.id;
    const params = {
      object_id: instanceId,
      object_type: type,
      limit: limit.join(','),
    };
    const orderAsString = orderBy
      .map((sort) => `${sort.field},${sort.direction}`)
      .join(',');

    if (orderAsString) {
      params.order_by = orderAsString;
    }
    return $.get('/api/related_assessments', params);
  },
});
