#ifndef _LINK_INFO_
#define _LINK_INFO_

#include <sys/types.h> 
#include <list>
#include <map>

struct LowerId;

template<class Key, class T>
class LinkInfoMap : public map<Key, T, LowerId> {
public:
	typedef map<Key, T, LowerId> baseMap;
	LinkInfoMap() : baseMap() {}

	// this next typedef of iterator seems extraneous but is required by gcc-2.96
	typedef typename map<Key, T, LowerId>::iterator iterator;
	typedef pair<iterator, bool> pair_iterator_bool;
	iterator insert(const Key & key, const T & item) {
		typename baseMap::value_type v(key, item);
		pair_iterator_bool ib = baseMap::insert(v);
		return ib.second ? ib.first : baseMap::end();
	}

	void eraseAll() { erase(baseMap::begin(), baseMap::end()); }

	T* findPtr(Key key) {
		iterator it;
		for (it = baseMap::begin(); it != baseMap::end(); it++)
			if (key == (*it).first)
				break;

		return (it == baseMap::end()) ? (T *)NULL : &((*it).second);
	}

	Key* findKey(T item) {
		iterator it;
		for (it = baseMap::begin(); it != baseMap::end(); it++)
			if (item == (*it).second)
				break;

		return (it == baseMap::end()) ? (Key *)NULL : &((*it).first);
	}

	void update(const Key & key, const T & item)
	{
		T* tptr = findPtr(key);
		if (tptr == NULL) {
			insert(key, item);
		}
		else {
			*tptr = item;
		}
	}
};

struct LinkInfo {
    datapathid dpsrc;
    datapathid dpdst;
    uint16_t sport;
    uint16_t dport;

	bool operator == (const LinkInfo & x ) {
		if ((dpsrc == x.dpsrc) && 
			(dpsrc == x.dpdst) && 
			(sport == x.sport) && 
			(dport == x.dport))
            return true;
		return false;
	}
};

struct LowerId {
	bool operator() (const LinkInfo & x, const LinkInfo & y) const
	{
		if (x.dpsrc < y.dpsrc)
			return true;
		else if ((x.dpsrc == y.dpsrc) && (x.dpdst < y.dpdst))
			return true;
		else
			return false;
	}
};

typedef list<LinkInfo> LinkInfoList;
typedef list<LinkInfo>::iterator LIL_iterator;

#endif
