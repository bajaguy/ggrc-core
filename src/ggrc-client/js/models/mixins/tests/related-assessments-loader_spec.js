/*
  Copyright (C) 2019 Google Inc.
  Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
*/

import {makeFakeInstance} from '../../../../js_specs/spec_helpers';
import Assessment from '../../business-models/assessment';
import Control from '../../business-models/control';
import Objective from '../../business-models/objective';
import Audit from '../../business-models/audit';
import Program from '../../business-models/program';
import Regulation from '../../business-models/regulation';
import System from '../../business-models/system';
import Issue from '../../business-models/issue';
import Requirement from '../../business-models/requirement';

const ENDPOINT = '/api/related_assessments';

describe('relatedAssessmentsLoader mixin', () => {
  beforeEach(() => {
    spyOn($, 'get');
  });

  describe('for Assessment model', () => {
    it('should contain getRelatedAssessments method', () => {
      const model = makeFakeInstance({model: Assessment})({});

      expect(model.getRelatedAssessments).toBeTruthy();
    });
  });

  describe('for Control model', () => {
    it('should contain getRelatedAssessments method', () => {
      const model = makeFakeInstance({model: Control})({});

      expect(model.getRelatedAssessments).toBeTruthy();
    });
  });

  describe('for Objective model', () => {
    it('should contain getRelatedAssessments method', () => {
      const model = makeFakeInstance({model: Objective})({});

      expect(model.getRelatedAssessments).toBeTruthy();
    });
  });

  describe('for Snapshot model', () => {
    it('should build correct response', () => {
      const model = makeFakeInstance({model: Control})({
        id: 1,
        type: 'Control',
        snapshot: {
          child_type: 'Control',
          child_id: 13,
          type: 'Snapshot',
        },
      });

      model.getRelatedAssessments();

      expect($.get).toHaveBeenCalledWith(ENDPOINT, {
        object_id: 13,
        object_type: 'Control',
        limit: '0,5',
      });
    });
  });

  describe('for other models', () => {
    it('should not contain getRelatedAssessments method', () => {
      const audit = makeFakeInstance({model: Audit})({});
      const program = makeFakeInstance({model: Program})({});
      const reg = makeFakeInstance({model: Regulation})({});
      const system = makeFakeInstance({model: System})({});
      const issue = makeFakeInstance({model: Issue})({});
      const requirement = makeFakeInstance({model: Requirement})({});

      expect(audit.getRelatedAssessments).toBeFalsy();
      expect(program.getRelatedAssessments).toBeFalsy();
      expect(reg.getRelatedAssessments).toBeFalsy();
      expect(system.getRelatedAssessments).toBeFalsy();
      expect(issue.getRelatedAssessments).toBeFalsy();
      expect(requirement.getRelatedAssessments).toBeFalsy();
    });
  });

  describe('when model is Assessment', () => {
    let fakeAssessmentCreator;

    beforeEach(function () {
      fakeAssessmentCreator = makeFakeInstance({model: Assessment});
    });


    it('should send default limit as "0,5"', () => {
      const model = fakeAssessmentCreator({id: 1, type: 'Assessment'});

      model.getRelatedAssessments();

      expect($.get).toHaveBeenCalledWith(ENDPOINT, {
        object_id: 1,
        object_type: 'Assessment',
        limit: '0,5',
      });
    });

    it('should send correct limit values', () => {
      const model = fakeAssessmentCreator({id: 1, type: 'Assessment'});

      model.getRelatedAssessments([0, 10]);

      expect($.get).toHaveBeenCalledWith(ENDPOINT, {
        object_id: 1,
        object_type: 'Assessment',
        limit: '0,10',
      });
    });

    it('should send correct order_by value', () => {
      const model = fakeAssessmentCreator({id: 1, type: 'Assessment'});

      model.getRelatedAssessments([0, 10], [{field: 'foo', direction: 'asc'}]);

      expect($.get).toHaveBeenCalledWith(ENDPOINT, {
        object_id: 1,
        object_type: 'Assessment',
        limit: '0,10',
        order_by: 'foo,asc',
      });
    });

    it('should send correct order_by value for multiple fields', () => {
      const model = fakeAssessmentCreator({id: 1, type: 'Assessment'});

      model.getRelatedAssessments([0, 10], [
        {field: 'foo', direction: 'asc'},
        {field: 'bar', direction: 'desc'},
      ]);

      expect($.get).toHaveBeenCalledWith(ENDPOINT, {
        object_id: 1,
        object_type: 'Assessment',
        limit: '0,10',
        order_by: 'foo,asc,bar,desc',
      });
    });
  });
});
