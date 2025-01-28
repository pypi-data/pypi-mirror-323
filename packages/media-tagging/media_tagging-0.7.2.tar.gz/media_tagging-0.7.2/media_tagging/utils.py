# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# pylint: disable=C0330, g-bad-import-order, g-multiple-import

"""Module for converting tables to TaggingResults."""

import itertools
import json
import os
from collections.abc import Sequence
from typing import Literal

import pandas as pd
import requests

from media_tagging import repositories, tagging_result


def convert_ids_to_knowledge_graph_names(
  knowledge_graph_ids: Sequence[str],
) -> dict[str, str]:
  api_key = os.getenv('KG_API_KEY')
  service_url = 'https://kgsearch.googleapis.com/v1/entities:search'
  batch_size = 100
  results = {}
  for ids in itertools.zip_longest(*[iter(knowledge_graph_ids)] * batch_size):
    params = {
      'ids': list(ids),
      'limit': batch_size,
      'key': api_key,
    }
    response = requests.get(service_url, params=params)
    data = json.loads(response.text)
    for element in data.get('itemListElement'):
      if result := element.get('result', {}):
        if kg_id := result.get('@id'):
          results[kg_id.replace('kg:', '')] = result.get('name')
  return results


def convert_table_to_tagging_result(
  table: pd.DataFrame,
  media_type: Literal['image', 'video', 'youtube_video'] = 'youtube_video',
) -> list[tagging_result.TaggingResult]:
  """Converts table data to tagging results."""
  knowledge_graph_mapping = convert_ids_to_knowledge_graph_names(
    set(table['tag'])
  )
  table['tags'] = table.apply(
    lambda row: tagging_result.Tag(
      name=knowledge_graph_mapping.get(row['tag'], row['tag']),
      score=row['score'],
    ),
    axis=1,
  )

  return [
    tagging_result.TaggingResult(
      identifier=media.media_url, type=media_type, content=media.tags
    )
    for _, media in table.groupby('media_url')
    .tags.apply(list)
    .reset_index()
    .iterrows()
  ]


db_url = 'sqlite:////home/amarkin/.filonov/internal.db'
repository = repositories.SqlAlchemyTaggingResultsRepository(db_url)
repository.initialize()
data = pd.read_csv('/home/amarkin/projects/filonov/internal/tags.csv')
results = convert_table_to_tagging_result(data)
tagged_media = {
  r.identifier for r in repository.get({r.identifier for r in results})
}
if new_results := {r for r in results if r.identifier not in tagged_media}:
  repository.add(new_results)
