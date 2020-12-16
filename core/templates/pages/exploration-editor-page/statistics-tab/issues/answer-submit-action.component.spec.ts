// Copyright 2020 The Oppia Authors. All Rights Reserved.
//
// Licensed under the Apache License, Version 2.0 (the 'License');
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//      http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an 'AS-IS' BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

/**
 * @fileoverview Unit tests for answerSubmitAction component.
 */

import { NO_ERRORS_SCHEMA } from '@angular/core';
import { async, ComponentFixture, TestBed } from '@angular/core/testing';
import { HtmlEscaperService } from 'services/html-escaper.service';
import { ExplorationHtmlFormatterService } from
  'services/exploration-html-formatter.service';
import { InteractionObjectFactory } from
  'domain/exploration/InteractionObjectFactory';
import { AnswerSubmitActionComponent } from './answer-submit-action.component';

describe('Answer Submit Action directive', () => {
  let component: AnswerSubmitActionComponent;
  let fixture: ComponentFixture<AnswerSubmitActionComponent>;
  var ctrl = null;
  var $scope = null;
  var explorationHtmlFormatterService = null;
  var htmlEscaperService = null;
  var interactionObjectFactory = null;

  beforeEach(() => {
    fixture = TestBed.createComponent(AnswerSubmitActionComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [AnswerSubmitActionComponent],
      providers: [
        {
          provide: explorationHtmlFormatterService,
          useClass: TestBed.get(ExplorationHtmlFormatterService)
        },
        {
          provide: htmlEscaperService
          useClass: TestBed.get(HtmlEscaperService);
        },
        {
        interactionObjectFactory = TestBed.get(InteractionObjectFactory)
        }
      }],
      schemas: [NO_ERRORS_SCHEMA]
    })
  }));

  beforeEach(angular.mock.module('oppia', ($provide) => {
    $provide.value('$attrs', {
      actionIndex: 2,
      answer: '"This is an answer string."',
      currentStateName: 'State name',
      destStateName: 'Introduction',
      interactionCustomizationArgs:
        `{
          "choices": {
            "value": [{
              "content_id": "",
              "html": "Value"
            }]
          },
          "showChoicesInShuffledOrder": {"value": true}
        }`,
      interactionId: 'MultipleChoiceInput',
      timeSpentInStateSecs: 2000
    });
  }));


  beforeEach(angular.mock.inject(($injector, $componentController) => {
    var $rootScope = $injector.get('$rootScope');

    $scope = $rootScope.$new();
    ctrl = $componentController('answerSubmitAction', {
      $scope: $scope,
      ExplorationHtmlFormatterService: explorationHtmlFormatterService,
      HtmlEscaperService: htmlEscaperService,
      InteractionObjectFactory: interactionObjectFactory
    });
    ctrl.$onInit();
  }));

  it('should initialize controller properties after its initialization',
    () => {
      expect(ctrl.currentStateName).toBe('State name');
      expect(ctrl.destStateName).toBe('Introduction');
      expect(ctrl.actionIndex).toBe(2);
      expect(ctrl.timeSpentInStateSecs).toBe(2000);
    });

  it('should get short answer html', () => {
    expect(ctrl.getShortAnswerHtml()).toBe(
      '<oppia-short-response-multiple-choice-input answer="&amp;quot;This is' +
      ' an answer string.&amp;quot;" choices="[&amp;quot;Value&amp;quot;]"' +
      '></oppia-short-response-multiple-choice-input>');
  });
});
