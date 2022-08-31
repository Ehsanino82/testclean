class jsonic(object):
    def __init__(self, *decor_args, **dec_key_words):
        self.dec_key_words = dec_key_words

    def __call__(self, fn):
        def jsoner(obj, **kwargs):
            dic = {}
            key = None
            the_dic = None
            recurse_limit = 2
            the_fields = obj._meta.get_all_field_names()
            kwargs.update(self.dec_key_words)

            recurse = kwargs.get('recurse', 0)
            incl = kwargs.get('include')
            sk = kwargs.get('skip')
            if incl:
                if type(incl) == type([]):
                    the_fields.extend(incl)
                else:
                    the_fields.append(incl)
            if sk:
                if type(sk) == type([]):
                    for skipper in sk:
                        if skipper in the_fields:
                            the_fields.remove(skipper)
                else:
                    if sk in the_fields:
                        the_fields.remove(sk)

            for f in the_fields:
                try:
                    the_dic = getattr(obj, "%s_set" % f)
                except AttributeError:
                    try:
                        the_dic = getattr(obj, f)
                    except AttributeError:
                        pass
                    except ObjectDoesNotExist:
                        pass
                    else:
                        key = str(f)
                except ObjectDoesNotExist:
                    pass
                else:
                    key = "%s_set" % f

                if key:
                    if hasattr(the_dic, "__class__") and hasattr(the_dic, "all"):
                        if callable(the_dic.all):
                            if hasattr(the_dic.all(), "json"):
                                if recurse < recurse_limit:
                                    kwargs['recurse'] = recurse + 1
                                    dic[key] = the_dic.all().json(**kwargs)
                    elif hasattr(the_dic, "json"):
                        if recurse < recurse_limit:
                            kwargs['recurse'] = recurse + 1
                            dic[key] = the_dic.json(**kwargs)
                    else:
                        try:
                            the_uni = the_dic.__str__()
                        except UnicodeEncodeError:
                            the_uni = the_dic.encode('utf-8')
                        dic[key] = the_uni

            if hasattr(obj, "_ik"):
                if hasattr(obj, obj._ik.image_field):
                    if hasattr(getattr(obj, obj._ik.image_field), 'size'):
                        if getattr(obj, obj._ik.image_field):
                            for ik_accessor in [getattr(obj, s.access_as) for s in obj._ik.specs]:
                                key = ik_accessor.spec.access_as
                                dic[key] = {
                                    'url': ik_accessor.url,
                                    'width': ik_accessor.width,
                                    'height': ik_accessor.height,
                                }
            return fn(obj, json=dic, **kwargs)

        return jsoner
