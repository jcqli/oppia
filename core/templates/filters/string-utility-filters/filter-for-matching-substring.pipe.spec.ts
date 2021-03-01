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

import { FilterForMatchingSubstringPipe } from
  'filters/string-utility-filters/filter-for-matching-substring.pipe';

describe('Testing FilterForMatchingSubstringPipe', () => {
  let pipe: FilterForMatchingSubstringPipe;
  beforeEach(() => {
    pipe = new FilterForMatchingSubstringPipe();
  });

  it('should have all expected pipes', () => {
    expect(pipe).not.toEqual(null);
  });

  it('should get items that contain search text', () => {
    let list = ['cat', 'dog', 'caterpillar'];
    expect(pipe.transform(list, 'cat')).toEqual(['cat', 'caterpillar']);
    expect(pipe.transform(list, 'dog')).toEqual(['dog']);
  });

  it('should not get items that do not contain search text', () => {
    let list = ['cat', 'dog', 'caterpillar'];
    expect(pipe.transform(list, 'puppy')).toEqual([]);
  });
});