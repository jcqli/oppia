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
 * @fileoverview Tests for CamelCaseToHyphens pipe for Oppia.
 */

import { FilterForMatchingTextPipe } from
  'filters/string-utility-filters/filter-for-matching-text.pipe';

describe('Testing FilterForMatchingTextPipe', () => {
  let pipe: FilterForMatchingTextPipe;
  beforeEach(() => {
    pipe = new FilterForMatchingTextPipe();
  });

  it('should have all expected pipes', () => {
    expect(pipe).not.toEqual(null);
  });

  it('should convert camelCase to hyphens properly', () => {
    let list = ["cat", "dog", "caterpillar"]
    expect(pipe.transform(list, "cat")).toEqual(["cat", "caterpillar"]);
    expect(pipe.transform(list, "dog")).toEqual(["dog"]);
  });
});
