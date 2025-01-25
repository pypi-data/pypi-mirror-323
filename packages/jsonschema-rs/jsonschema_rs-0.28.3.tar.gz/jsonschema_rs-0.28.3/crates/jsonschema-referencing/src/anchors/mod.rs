use std::sync::Arc;

use serde_json::Value;

mod keys;

use crate::{Draft, Error, Resolved, Resolver, Resource};
pub(crate) use keys::{AnchorKey, AnchorKeyRef};

/// An anchor within a resource.
#[derive(Debug, Clone, PartialEq, Eq)]
pub(crate) enum Anchor {
    Default {
        draft: Draft,
        name: String,
        resource: Arc<Resource>,
    },
    /// Dynamic anchors from Draft 2020-12.
    Dynamic {
        draft: Draft,
        name: String,
        resource: Arc<Resource>,
    },
}

impl Anchor {
    /// Anchor's name.
    pub(crate) fn name(&self) -> &str {
        match self {
            Anchor::Default { name, .. } | Anchor::Dynamic { name, .. } => name,
        }
    }
    /// Get the resource for this anchor.
    pub(crate) fn resolve<'r>(&'r self, resolver: Resolver<'r>) -> Result<Resolved<'r>, Error> {
        match self {
            Anchor::Default { resource, .. } => Ok(Resolved::new(
                resource.contents(),
                resolver,
                resource.draft(),
            )),
            Anchor::Dynamic { name, resource, .. } => {
                let mut last = resource;
                for uri in &resolver.dynamic_scope() {
                    match resolver.registry.anchor(uri, name) {
                        Ok(anchor) => {
                            if let Anchor::Dynamic { resource, .. } = anchor {
                                last = resource;
                            }
                        }
                        Err(Error::NoSuchAnchor { .. }) => continue,
                        Err(err) => return Err(err),
                    }
                }
                Ok(Resolved::new(
                    last.contents(),
                    resolver.in_subresource((**last).as_ref())?,
                    last.draft(),
                ))
            }
        }
    }
}

pub(crate) fn anchor(draft: Draft, contents: &Value) -> Box<dyn Iterator<Item = Anchor> + '_> {
    Box::new(contents.as_object().into_iter().flat_map(move |schema| {
        let default_anchor =
            schema
                .get("$anchor")
                .and_then(Value::as_str)
                .map(|name| Anchor::Default {
                    draft,
                    name: name.to_string(),
                    resource: Arc::new(draft.create_resource(contents.clone())),
                });

        let dynamic_anchor = schema
            .get("$dynamicAnchor")
            .and_then(Value::as_str)
            .map(|name| Anchor::Dynamic {
                draft,
                name: name.to_string(),
                resource: Arc::new(draft.create_resource(contents.clone())),
            });

        default_anchor.into_iter().chain(dynamic_anchor)
    }))
}

pub(crate) fn anchor_2019(draft: Draft, contents: &Value) -> Box<dyn Iterator<Item = Anchor>> {
    Box::new(
        contents
            .as_object()
            .and_then(|schema| schema.get("$anchor").and_then(Value::as_str))
            .map(move |name| Anchor::Default {
                draft,
                name: name.to_string(),
                resource: Arc::new(draft.create_resource(contents.clone())),
            })
            .into_iter(),
    )
}

pub(crate) fn legacy_anchor_in_dollar_id(
    draft: Draft,
    contents: &Value,
) -> Box<dyn Iterator<Item = Anchor>> {
    Box::new(
        contents
            .as_object()
            .and_then(|schema| schema.get("$id").and_then(Value::as_str))
            .and_then(|id| id.strip_prefix('#'))
            .map(move |id| Anchor::Default {
                draft,
                name: id.to_string(),
                resource: Arc::new(draft.create_resource(contents.clone())),
            })
            .into_iter(),
    )
}

pub(crate) fn legacy_anchor_in_id<'a>(
    draft: Draft,
    contents: &'a Value,
) -> Box<dyn Iterator<Item = Anchor> + 'a> {
    Box::new(
        contents
            .as_object()
            .and_then(|schema| schema.get("id").and_then(Value::as_str))
            .and_then(|id| id.strip_prefix('#'))
            .map(move |id| Anchor::Default {
                draft,
                name: id.to_string(),
                resource: Arc::new(draft.create_resource(contents.clone())),
            })
            .into_iter(),
    )
}

#[cfg(test)]
mod tests {
    use crate::{Draft, Registry};
    use serde_json::json;

    #[test]
    fn test_lookup_trivial_dynamic_ref() {
        let one = Draft::Draft202012.create_resource(json!({"$dynamicAnchor": "foo"}));
        let registry =
            Registry::try_new("http://example.com", one.clone()).expect("Invalid resources");
        let resolver = registry
            .try_resolver("http://example.com")
            .expect("Invalid base URI");
        let resolved = resolver.lookup("#foo").expect("Lookup failed");
        assert_eq!(resolved.contents(), one.contents());
    }

    #[test]
    fn test_multiple_lookup_trivial_dynamic_ref() {
        let true_resource = Draft::Draft202012.create_resource(json!(true));
        let root = Draft::Draft202012.create_resource(json!({
            "$id": "http://example.com",
            "$dynamicAnchor": "fooAnchor",
            "$defs": {
                "foo": {
                    "$id": "foo",
                    "$dynamicAnchor": "fooAnchor",
                    "$defs": {
                        "bar": true,
                        "baz": {
                            "$dynamicAnchor": "fooAnchor",
                        },
                    },
                },
            },
        }));

        let registry = Registry::try_from_resources(
            [
                ("http://example.com".to_string(), root.clone()),
                ("http://example.com/foo/".to_string(), true_resource),
                ("http://example.com/foo/bar".to_string(), root.clone()),
            ]
            .into_iter(),
        )
        .expect("Invalid resources");
        let resolver = registry
            .try_resolver("http://example.com")
            .expect("Invalid base URI");

        let first = resolver.lookup("").expect("Lookup failed");
        let second = first.resolver().lookup("foo/").expect("Lookup failed");
        let third = second.resolver().lookup("bar").expect("Lookup failed");
        let fourth = third
            .resolver()
            .lookup("#fooAnchor")
            .expect("Lookup failed");
        assert_eq!(fourth.contents(), root.contents());
        assert_eq!(format!("{:?}", fourth.resolver()), "Resolver { base_uri: \"http://example.com\", scopes: \"[http://example.com/foo/, http://example.com, http://example.com]\" }");
    }

    #[test]
    fn test_multiple_lookup_dynamic_ref_to_nondynamic_ref() {
        let one = Draft::Draft202012.create_resource(json!({"$anchor": "fooAnchor"}));
        let two = Draft::Draft202012.create_resource(json!({
            "$id": "http://example.com",
            "$dynamicAnchor": "fooAnchor",
            "$defs": {
                "foo": {
                    "$id": "foo",
                    "$dynamicAnchor": "fooAnchor",
                    "$defs": {
                        "bar": true,
                        "baz": {
                            "$dynamicAnchor": "fooAnchor",
                        },
                    },
                },
            },
        }));

        let registry = Registry::try_from_resources(
            [
                ("http://example.com".to_string(), two.clone()),
                ("http://example.com/foo/".to_string(), one),
                ("http://example.com/foo/bar".to_string(), two.clone()),
            ]
            .into_iter(),
        )
        .expect("Invalid resources");
        let resolver = registry
            .try_resolver("http://example.com")
            .expect("Invalid base URI");

        let first = resolver.lookup("").expect("Lookup failed");
        let second = first.resolver().lookup("foo/").expect("Lookup failed");
        let third = second.resolver().lookup("bar").expect("Lookup failed");
        let fourth = third
            .resolver()
            .lookup("#fooAnchor")
            .expect("Lookup failed");
        assert_eq!(fourth.contents(), two.contents());
    }

    #[test]
    fn test_unknown_anchor() {
        let schema = Draft::Draft202012.create_resource(json!({
            "$defs": {
                "foo": { "$anchor": "knownAnchor" }
            }
        }));
        let registry = Registry::try_new("http://example.com", schema).expect("Invalid resources");
        let resolver = registry
            .try_resolver("http://example.com")
            .expect("Invalid base URI");

        let result = resolver.lookup("#unknownAnchor");
        assert_eq!(
            result.unwrap_err().to_string(),
            "Anchor 'unknownAnchor' does not exist"
        );
    }

    #[test]
    fn test_invalid_anchor_with_slash() {
        let schema = Draft::Draft202012.create_resource(json!({
            "$defs": {
                "foo": { "$anchor": "knownAnchor" }
            }
        }));
        let registry = Registry::try_new("http://example.com", schema).expect("Invalid resources");
        let resolver = registry
            .try_resolver("http://example.com")
            .expect("Invalid base URI");

        let result = resolver.lookup("#invalid/anchor");
        assert_eq!(
            result.unwrap_err().to_string(),
            "Anchor 'invalid/anchor' is invalid"
        );
    }

    #[test]
    fn test_lookup_trivial_recursive_ref() {
        let one = Draft::Draft201909.create_resource(json!({"$recursiveAnchor": true}));
        let registry =
            Registry::try_new("http://example.com", one.clone()).expect("Invalid resources");
        let resolver = registry
            .try_resolver("http://example.com")
            .expect("Invalid base URI");
        let first = resolver.lookup("").expect("Lookup failed");
        let resolved = first
            .resolver()
            .lookup_recursive_ref()
            .expect("Lookup failed");
        assert_eq!(resolved.contents(), one.contents());
    }

    #[test]
    fn test_lookup_recursive_ref_to_bool() {
        let true_resource = Draft::Draft201909.create_resource(json!(true));
        let registry = Registry::try_new("http://example.com", true_resource.clone())
            .expect("Invalid resources");
        let resolver = registry
            .try_resolver("http://example.com")
            .expect("Invalid base URI");
        let resolved = resolver.lookup_recursive_ref().expect("Lookup failed");
        assert_eq!(resolved.contents(), true_resource.contents());
    }

    #[test]
    fn test_multiple_lookup_recursive_ref_to_bool() {
        let true_resource = Draft::Draft201909.create_resource(json!(true));
        let root = Draft::Draft201909.create_resource(json!({
            "$id": "http://example.com",
            "$recursiveAnchor": true,
            "$defs": {
                "foo": {
                    "$id": "foo",
                    "$recursiveAnchor": true,
                    "$defs": {
                        "bar": true,
                        "baz": {
                            "$recursiveAnchor": true,
                            "$anchor": "fooAnchor",
                        },
                    },
                },
            },
        }));

        let registry = Registry::try_from_resources(
            vec![
                ("http://example.com".to_string(), root.clone()),
                ("http://example.com/foo/".to_string(), true_resource),
                ("http://example.com/foo/bar".to_string(), root.clone()),
            ]
            .into_iter(),
        )
        .expect("Invalid resources");

        let resolver = registry
            .try_resolver("http://example.com")
            .expect("Invalid base URI");
        let first = resolver.lookup("").expect("Lookup failed");
        let second = first.resolver().lookup("foo/").expect("Lookup failed");
        let third = second.resolver().lookup("bar").expect("Lookup failed");
        let fourth = third
            .resolver()
            .lookup_recursive_ref()
            .expect("Lookup failed");
        assert_eq!(fourth.contents(), root.contents());
    }

    #[test]
    fn test_multiple_lookup_recursive_ref_with_nonrecursive_ref() {
        let one = Draft::Draft201909.create_resource(json!({"$recursiveAnchor": true}));
        let two = Draft::Draft201909.create_resource(json!({
            "$id": "http://example.com",
            "$recursiveAnchor": true,
            "$defs": {
                "foo": {
                    "$id": "foo",
                    "$recursiveAnchor": true,
                    "$defs": {
                        "bar": true,
                        "baz": {
                            "$recursiveAnchor": true,
                            "$anchor": "fooAnchor",
                        },
                    },
                },
            },
        }));
        let three = Draft::Draft201909.create_resource(json!({"$recursiveAnchor": false}));

        let registry = Registry::try_from_resources(
            vec![
                ("http://example.com".to_string(), three),
                ("http://example.com/foo/".to_string(), two.clone()),
                ("http://example.com/foo/bar".to_string(), one),
            ]
            .into_iter(),
        )
        .expect("Invalid resources");

        let resolver = registry
            .try_resolver("http://example.com")
            .expect("Invalid base URI");
        let first = resolver.lookup("").expect("Lookup failed");
        let second = first.resolver().lookup("foo/").expect("Lookup failed");
        let third = second.resolver().lookup("bar").expect("Lookup failed");
        let fourth = third
            .resolver()
            .lookup_recursive_ref()
            .expect("Lookup failed");
        assert_eq!(fourth.contents(), two.contents());
    }
}
