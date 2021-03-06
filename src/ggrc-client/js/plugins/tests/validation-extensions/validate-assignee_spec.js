/*
  Copyright (C) 2019 Google Inc.
  Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
*/

import CanList from 'can-list/can-list';
import CanModel from 'can-model/src/can-model';

import * as aclUtils from '../../utils/acl-utils';

describe('validateAssignee extension', () => {
  let TestModel;

  beforeAll(() => {
    TestModel = CanModel.extend({}, {
      define: {
        access_control_list: {
          value: new CanList([]),
          validate: {
            validateAssignee: 'CycleTaskGroupObjectTask',
          },
        },
      },
    });
  });
  it('should return TRUE', () => {
    const instance = new TestModel();
    const acl = new CanList([{ac_role_id: 10}, {ac_role_id: 5}]);
    instance.attr('access_control_list', acl);
    spyOn(aclUtils, 'getRole').and.returnValue({id: 5});

    expect(instance.validate()).toBeTruthy();
  });
  it('should return FALSE, because ACL is empty', () => {
    const instance = new TestModel();
    const acl = new CanList([]);
    instance.attr('access_control_list', acl);
    spyOn(aclUtils, 'getRole').and.returnValue({id: 5});

    expect(instance.validate()).toBeFalsy();
  });
  it('should return FALSE, because ACL does not contain role', () => {
    const instance = new TestModel();
    const acl = new CanList([{ac_role_id: 10}]);
    instance.attr('access_control_list', acl);
    spyOn(aclUtils, 'getRole').and.returnValue({id: 5});

    expect(instance.validate()).toBeFalsy();
  });
  it('should return FALSE, because "getRole" returns undefined', () => {
    const instance = new TestModel();
    const acl = new CanList([{ac_role_id: 10}]);
    instance.attr('access_control_list', acl);

    spyOn(aclUtils, 'getRole').and.returnValue(undefined);
    expect(instance.validate()).toBeFalsy();
  });
});
