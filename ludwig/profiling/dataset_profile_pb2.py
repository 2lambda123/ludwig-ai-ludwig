# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: dataset_profile.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder

# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from google.protobuf import any_pb2 as google_dot_protobuf_dot_any__pb2
from google.protobuf import struct_pb2 as google_dot_protobuf_dot_struct__pb2

DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(
    b'\n\x15\x64\x61taset_profile.proto\x12\tludwigwhy\x1a\x19google/protobuf/any.proto\x1a\x1cgoogle/protobuf/struct.proto"\x88\x01\n\x08\x44\x61taType\x12&\n\x04type\x18\x01 \x01(\x0e\x32\x18.ludwigwhy.DataType.Type"T\n\x04Type\x12\x0b\n\x07UNKNOWN\x10\x00\x12\x08\n\x04NULL\x10\x01\x12\x0e\n\nFRACTIONAL\x10\x02\x12\x0c\n\x08INTEGRAL\x10\x03\x12\x0b\n\x07\x42OOLEAN\x10\x04\x12\n\n\x06STRING\x10\x05""\n\x10HllSketchMessage\x12\x0e\n\x06sketch\x18\x01 \x01(\x0c",\n\x1a\x46requentItemsSketchMessage\x12\x0e\n\x06sketch\x18\x01 \x01(\x0c""\n\x10KllSketchMessage\x12\x0e\n\x06sketch\x18\x01 \x01(\x0c""\n\x10\x43pcSketchMessage\x12\x0e\n\x06sketch\x18\x01 \x01(\x0c"\x86\x03\n\x16MetricComponentMessage\x12\x0f\n\x07type_id\x18\x01 \x01(\r\x12\x0b\n\x01n\x18\x02 \x01(\x03H\x00\x12\x0b\n\x01\x64\x18\x03 \x01(\x01H\x00\x12?\n\x0e\x66requent_items\x18\x04 \x01(\x0b\x32%.ludwigwhy.FrequentItemsSketchMessageH\x00\x12*\n\x03hll\x18\x05 \x01(\x0b\x32\x1b.ludwigwhy.HllSketchMessageH\x00\x12*\n\x03kll\x18\x06 \x01(\x0b\x32\x1b.ludwigwhy.KllSketchMessageH\x00\x12*\n\x03\x63pc\x18\x07 \x01(\x0b\x32\x1b.ludwigwhy.CpcSketchMessageH\x00\x12\x1a\n\x10serialized_bytes\x18\n \x01(\x0cH\x00\x12\x32\n\x0f\x64\x61taclass_param\x18\x0b \x01(\x0b\x32\x17.google.protobuf.StructH\x00\x12#\n\x03msg\x18\x0c \x01(\x0b\x32\x14.google.protobuf.AnyH\x00\x42\x07\n\x05value"\xb6\x01\n\rMetricMessage\x12I\n\x11metric_components\x18\x01 \x03(\x0b\x32..ludwigwhy.MetricMessage.MetricComponentsEntry\x1aZ\n\x15MetricComponentsEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\x30\n\x05value\x18\x02 \x01(\x0b\x32!.ludwigwhy.MetricComponentMessage:\x02\x38\x01"\xb6\x01\n\rColumnMessage\x12I\n\x11metric_components\x18\x01 \x03(\x0b\x32..ludwigwhy.ColumnMessage.MetricComponentsEntry\x1aZ\n\x15MetricComponentsEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\x30\n\x05value\x18\x02 \x01(\x0b\x32!.ludwigwhy.MetricComponentMessage:\x02\x38\x01"\xd8\x02\n\x11\x44\x61tasetProperties\x12\x1c\n\x14schema_major_version\x18\x01 \x01(\r\x12\x1c\n\x14schema_minor_version\x18\x02 \x01(\r\x12\x1a\n\x12\x63reation_timestamp\x18\x04 \x01(\x04\x12\x19\n\x11\x64\x61taset_timestamp\x18\x05 \x01(\x04\x12\x34\n\x04tags\x18\x06 \x03(\x0b\x32&.ludwigwhy.DatasetProperties.TagsEntry\x12<\n\x08metadata\x18\x07 \x03(\x0b\x32*.ludwigwhy.DatasetProperties.MetadataEntry\x1a+\n\tTagsEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\r\n\x05value\x18\x02 \x01(\t:\x02\x38\x01\x1a/\n\rMetadataEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\r\n\x05value\x18\x02 \x01(\t:\x02\x38\x01"\x1f\n\x0c\x43hunkOffsets\x12\x0f\n\x07offsets\x18\x01 \x03(\x04"\xb4\x01\n\x0c\x43hunkMessage\x12H\n\x11metric_components\x18\x01 \x03(\x0b\x32-.ludwigwhy.ChunkMessage.MetricComponentsEntry\x1aZ\n\x15MetricComponentsEntry\x12\x0b\n\x03key\x18\x01 \x01(\r\x12\x30\n\x05value\x18\x02 \x01(\x0b\x32!.ludwigwhy.MetricComponentMessage:\x02\x38\x01"\x80\x01\n\x0b\x43hunkHeader\x12.\n\x04type\x18\x01 \x01(\x0e\x32 .ludwigwhy.ChunkHeader.ChunkType\x12\x0b\n\x03tag\x18\x02 \x01(\t\x12\x0e\n\x06length\x18\x03 \x01(\r"$\n\tChunkType\x12\x0b\n\x07\x44\x41TASET\x10\x00\x12\n\n\x06\x43OLUMN\x10\x02"\xb6\x03\n\x14\x44\x61tasetProfileHeader\x12\x30\n\nproperties\x18\x01 \x01(\x0b\x32\x1c.ludwigwhy.DatasetProperties\x12J\n\x0e\x63olumn_offsets\x18\x02 \x03(\x0b\x32\x32.ludwigwhy.DatasetProfileHeader.ColumnOffsetsEntry\x12/\n\x0emetric_offsets\x18\x03 \x03(\x0b\x32\x17.ludwigwhy.ChunkOffsets\x12\x0e\n\x06length\x18\x04 \x01(\x04\x12U\n\x14indexed_metric_paths\x18\x05 \x03(\x0b\x32\x37.ludwigwhy.DatasetProfileHeader.IndexedMetricPathsEntry\x1aM\n\x12\x43olumnOffsetsEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12&\n\x05value\x18\x02 \x01(\x0b\x32\x17.ludwigwhy.ChunkOffsets:\x02\x38\x01\x1a\x39\n\x17IndexedMetricPathsEntry\x12\x0b\n\x03key\x18\x01 \x01(\r\x12\r\n\x05value\x18\x02 \x01(\t:\x02\x38\x01"(\n\nSegmentTag\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\r\n\x05value\x18\x02 \x01(\t".\n\x07Segment\x12#\n\x04tags\x18\x01 \x03(\x0b\x32\x15.ludwigwhy.SegmentTag"\xc1\x01\n\x14\x44\x61tasetSegmentHeader\x12\x14\n\x0chas_segments\x18\x01 \x01(\x08\x12$\n\x08segments\x18\x04 \x03(\x0b\x32\x12.ludwigwhy.Segment\x12=\n\x07offsets\x18\x05 \x03(\x0b\x32,.ludwigwhy.DatasetSegmentHeader.OffsetsEntry\x1a.\n\x0cOffsetsEntry\x12\x0b\n\x03key\x18\x01 \x01(\r\x12\r\n\x05value\x18\x02 \x01(\x04:\x02\x38\x01"\xea\x01\n\x0e\x44\x61tasetProfile\x12\x11\n\ttimestamp\x18\x01 \x01(\x03\x12\x14\n\x0cnum_examples\x18\x02 \x01(\x03\x12\x12\n\nsize_bytes\x18\x03 \x01(\x03\x12H\n\x10\x66\x65\x61ture_profiles\x18\x14 \x03(\x0b\x32..ludwigwhy.DatasetProfile.FeatureProfilesEntry\x1aQ\n\x14\x46\x65\x61tureProfilesEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12(\n\x05value\x18\x02 \x01(\x0b\x32\x19.ludwigwhy.FeatureProfile:\x02\x38\x01"C\n\x0e\x46\x65\x61tureProfile\x12\x31\n\x0fwhylogs_metrics\x18\x01 \x01(\x0b\x32\x18.ludwigwhy.ColumnMessageb\x06proto3'
)

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, "dataset_profile_pb2", globals())
if _descriptor._USE_C_DESCRIPTORS == False:

    DESCRIPTOR._options = None
    _METRICMESSAGE_METRICCOMPONENTSENTRY._options = None
    _METRICMESSAGE_METRICCOMPONENTSENTRY._serialized_options = b"8\001"
    _COLUMNMESSAGE_METRICCOMPONENTSENTRY._options = None
    _COLUMNMESSAGE_METRICCOMPONENTSENTRY._serialized_options = b"8\001"
    _DATASETPROPERTIES_TAGSENTRY._options = None
    _DATASETPROPERTIES_TAGSENTRY._serialized_options = b"8\001"
    _DATASETPROPERTIES_METADATAENTRY._options = None
    _DATASETPROPERTIES_METADATAENTRY._serialized_options = b"8\001"
    _CHUNKMESSAGE_METRICCOMPONENTSENTRY._options = None
    _CHUNKMESSAGE_METRICCOMPONENTSENTRY._serialized_options = b"8\001"
    _DATASETPROFILEHEADER_COLUMNOFFSETSENTRY._options = None
    _DATASETPROFILEHEADER_COLUMNOFFSETSENTRY._serialized_options = b"8\001"
    _DATASETPROFILEHEADER_INDEXEDMETRICPATHSENTRY._options = None
    _DATASETPROFILEHEADER_INDEXEDMETRICPATHSENTRY._serialized_options = b"8\001"
    _DATASETSEGMENTHEADER_OFFSETSENTRY._options = None
    _DATASETSEGMENTHEADER_OFFSETSENTRY._serialized_options = b"8\001"
    _DATASETPROFILE_FEATUREPROFILESENTRY._options = None
    _DATASETPROFILE_FEATUREPROFILESENTRY._serialized_options = b"8\001"
    _DATATYPE._serialized_start = 94
    _DATATYPE._serialized_end = 230
    _DATATYPE_TYPE._serialized_start = 146
    _DATATYPE_TYPE._serialized_end = 230
    _HLLSKETCHMESSAGE._serialized_start = 232
    _HLLSKETCHMESSAGE._serialized_end = 266
    _FREQUENTITEMSSKETCHMESSAGE._serialized_start = 268
    _FREQUENTITEMSSKETCHMESSAGE._serialized_end = 312
    _KLLSKETCHMESSAGE._serialized_start = 314
    _KLLSKETCHMESSAGE._serialized_end = 348
    _CPCSKETCHMESSAGE._serialized_start = 350
    _CPCSKETCHMESSAGE._serialized_end = 384
    _METRICCOMPONENTMESSAGE._serialized_start = 387
    _METRICCOMPONENTMESSAGE._serialized_end = 777
    _METRICMESSAGE._serialized_start = 780
    _METRICMESSAGE._serialized_end = 962
    _METRICMESSAGE_METRICCOMPONENTSENTRY._serialized_start = 872
    _METRICMESSAGE_METRICCOMPONENTSENTRY._serialized_end = 962
    _COLUMNMESSAGE._serialized_start = 965
    _COLUMNMESSAGE._serialized_end = 1147
    _COLUMNMESSAGE_METRICCOMPONENTSENTRY._serialized_start = 872
    _COLUMNMESSAGE_METRICCOMPONENTSENTRY._serialized_end = 962
    _DATASETPROPERTIES._serialized_start = 1150
    _DATASETPROPERTIES._serialized_end = 1494
    _DATASETPROPERTIES_TAGSENTRY._serialized_start = 1402
    _DATASETPROPERTIES_TAGSENTRY._serialized_end = 1445
    _DATASETPROPERTIES_METADATAENTRY._serialized_start = 1447
    _DATASETPROPERTIES_METADATAENTRY._serialized_end = 1494
    _CHUNKOFFSETS._serialized_start = 1496
    _CHUNKOFFSETS._serialized_end = 1527
    _CHUNKMESSAGE._serialized_start = 1530
    _CHUNKMESSAGE._serialized_end = 1710
    _CHUNKMESSAGE_METRICCOMPONENTSENTRY._serialized_start = 1620
    _CHUNKMESSAGE_METRICCOMPONENTSENTRY._serialized_end = 1710
    _CHUNKHEADER._serialized_start = 1713
    _CHUNKHEADER._serialized_end = 1841
    _CHUNKHEADER_CHUNKTYPE._serialized_start = 1805
    _CHUNKHEADER_CHUNKTYPE._serialized_end = 1841
    _DATASETPROFILEHEADER._serialized_start = 1844
    _DATASETPROFILEHEADER._serialized_end = 2282
    _DATASETPROFILEHEADER_COLUMNOFFSETSENTRY._serialized_start = 2146
    _DATASETPROFILEHEADER_COLUMNOFFSETSENTRY._serialized_end = 2223
    _DATASETPROFILEHEADER_INDEXEDMETRICPATHSENTRY._serialized_start = 2225
    _DATASETPROFILEHEADER_INDEXEDMETRICPATHSENTRY._serialized_end = 2282
    _SEGMENTTAG._serialized_start = 2284
    _SEGMENTTAG._serialized_end = 2324
    _SEGMENT._serialized_start = 2326
    _SEGMENT._serialized_end = 2372
    _DATASETSEGMENTHEADER._serialized_start = 2375
    _DATASETSEGMENTHEADER._serialized_end = 2568
    _DATASETSEGMENTHEADER_OFFSETSENTRY._serialized_start = 2522
    _DATASETSEGMENTHEADER_OFFSETSENTRY._serialized_end = 2568
    _DATASETPROFILE._serialized_start = 2571
    _DATASETPROFILE._serialized_end = 2805
    _DATASETPROFILE_FEATUREPROFILESENTRY._serialized_start = 2724
    _DATASETPROFILE_FEATUREPROFILESENTRY._serialized_end = 2805
    _FEATUREPROFILE._serialized_start = 2807
    _FEATUREPROFILE._serialized_end = 2874
# @@protoc_insertion_point(module_scope)
