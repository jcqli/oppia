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

import { waitForAsync, TestBed, ComponentFixture } from '@angular/core/testing';
import { AnswerSubmitActionComponent } from './answer-submit-action.component';
import { NO_ERRORS_SCHEMA } from '@angular/core';
import { InteractionObjectFactory } from 'domain/exploration/InteractionObjectFactory';
import { ExplorationHtmlFormatterService } from 'services/exploration-html-formatter.service';
import { HtmlEscaperService } from 'services/html-escaper.service';

let component: AnswerSubmitActionComponent;
let fixture: ComponentFixture<AnswerSubmitActionComponent>;

describe('Answer Submit Action directive', () => {
  let actionIndex = 2;
  let answer = '"This is an answer string."';
  let currentStateName = 'State name';
  let destStateName = 'Introduction';
  let interactionCustomizationArgs = `{
    "choices": {
      "value": [{
        "content_id": "",
        "html": "Value"
      }]
    },
    "showChoicesInShuffledOrder": {"value": true}
  }`;
  let interactionId = 'MultipleChoiceInput';
  let timeSpentInStateSecs: 2000

  beforeEach(waitForAsync(() => {
    TestBed.configureTestingModule({
      declarations: [AnswerSubmitActionComponent],
      providers: [
        ExplorationHtmlFormatterService,
        HtmlEscaperService,
        InteractionObjectFactory
      ],
      schemas: [NO_ERRORS_SCHEMA]
    }).compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(AnswerSubmitActionComponent);
    component = fixture.componentInstance;
    component.actionIndex = actionIndex;
    component.answer = answer;
    component.currentStateName = currentStateName;
    component.destStateName = destStateName;
    component.interactionCustomizationArgs = interactionCustomizationArgs;
    component.interactionId = interactionId;
    component.timeSpentInStateSecs = timeSpentInStateSecs;
    fixture.detectChanges();
  });

  it('should initialize controller properties after its initialization',
    () => {
      expect(component.currentStateName).toBe('State name');
      expect(component.destStateName).toBe('Introduction');
      expect(component.actionIndex).toBe(2);
      expect(component.timeSpentInStateSecs).toBe(2000);
    });

  it('should get short answer html', () => {
    expect(component.getShortAnswerHtml()).toBe(
      '<oppia-short-response-multiple-choice-input answer="&amp;quot;This is' +
      ' an answer string.&amp;quot;" choices="[&amp;quot;Value&amp;quot;]"' +
      '></oppia-short-response-multiple-choice-input>');
  });
});
