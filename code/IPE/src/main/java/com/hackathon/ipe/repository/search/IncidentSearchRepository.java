package com.hackathon.ipe.repository.search;

import co.elastic.clients.elasticsearch._types.query_dsl.QueryStringQuery;
import com.hackathon.ipe.domain.Incident;
import com.hackathon.ipe.repository.IncidentRepository;
import java.util.List;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageImpl;
import org.springframework.data.domain.Pageable;
import org.springframework.data.elasticsearch.client.elc.ElasticsearchTemplate;
import org.springframework.data.elasticsearch.client.elc.NativeQuery;
import org.springframework.data.elasticsearch.core.SearchHit;
import org.springframework.data.elasticsearch.core.SearchHits;
import org.springframework.data.elasticsearch.core.query.Query;
import org.springframework.data.elasticsearch.repository.ElasticsearchRepository;
import org.springframework.scheduling.annotation.Async;

/**
 * Spring Data Elasticsearch repository for the {@link Incident} entity.
 */
public interface IncidentSearchRepository extends ElasticsearchRepository<Incident, Long>, IncidentSearchRepositoryInternal {}

interface IncidentSearchRepositoryInternal {
    Page<Incident> search(String query, Pageable pageable);

    Page<Incident> search(Query query);

    @Async
    void index(Incident entity);

    @Async
    void deleteFromIndexById(Long id);
}

class IncidentSearchRepositoryInternalImpl implements IncidentSearchRepositoryInternal {

    private final ElasticsearchTemplate elasticsearchTemplate;
    private final IncidentRepository repository;

    IncidentSearchRepositoryInternalImpl(ElasticsearchTemplate elasticsearchTemplate, IncidentRepository repository) {
        this.elasticsearchTemplate = elasticsearchTemplate;
        this.repository = repository;
    }

    @Override
    public Page<Incident> search(String query, Pageable pageable) {
        NativeQuery nativeQuery = new NativeQuery(QueryStringQuery.of(qs -> qs.query(query))._toQuery());
        return search(nativeQuery.setPageable(pageable));
    }

    @Override
    public Page<Incident> search(Query query) {
        SearchHits<Incident> searchHits = elasticsearchTemplate.search(query, Incident.class);
        List<Incident> hits = searchHits.map(SearchHit::getContent).stream().toList();
        return new PageImpl<>(hits, query.getPageable(), searchHits.getTotalHits());
    }

    @Override
    public void index(Incident entity) {
        repository.findById(entity.getId()).ifPresent(elasticsearchTemplate::save);
    }

    @Override
    public void deleteFromIndexById(Long id) {
        elasticsearchTemplate.delete(String.valueOf(id), Incident.class);
    }
}
