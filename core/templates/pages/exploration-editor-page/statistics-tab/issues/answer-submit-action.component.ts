// Copyright 2019 The Oppia Authors. All Rights Reserved.
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//      http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS-IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

/**
 * @fileoverview Component for the Answer Submit Learner Action.
 */

import { Component, Input, OnInit } from '@angular/core';
import { downgradeComponent } from '@angular/upgrade/static';
import { InteractionObjectFactory } from 'domain/exploration/InteractionObjectFactory.ts';
import { ExplorationHtmlFormatterService } from 'services/exploration-html-formatter.service.ts';
import { HtmlEscaperService } from 'services/html-escaper.service.ts';

@Component({
  selector: 'answer-submit-action',
  templateUrl: './answer-submit-action.component.html',
  styleUrls: []
})
export class AnswerSubmitActionComponent implements OnInit {
  @Input() currentStateName: string;
  @Input() destStateName: string;
  @Input() actionIndex: number;
  @Input() timeSpentInStateSecs: number;
  @Input() interactionId: string = '';
  @Input() interactionCustomizationArgs: string = '';
  @Input() answer: string = '';
  _customizationArgs = (
    this.interactionObjectFactory.convertFromCustomizationArgsBackendDict(
      this.interactionId,
      this.htmlEscaperService.escapedJsonToObj(
        this.interactionCustomizationArgs)
    )
  );
  _answer: number = this.htmlEscaperService.escapedJsonToObj(
    this.answer) as number;

  constructor(
    private explorationHtmlFormatterService: ExplorationHtmlFormatterService,
    private htmlEscaperService: HtmlEscaperService,
    private interactionObjectFactory: InteractionObjectFactory
  ) {}

  ngOnInit(): void {
  }

  getShortAnswerHtml(): string {
    return this.explorationHtmlFormatterService.getShortAnswerHtml(
      this._answer,
      this.interactionId,
      this._customizationArgs);
  }
}
angular.module('oppia').directive(
  'answerSubmitAction', downgradeComponent(
    { component: AnswerSubmitActionComponent }
  )
);
