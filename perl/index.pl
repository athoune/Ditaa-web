#!/usr/bin/env perl
use Mojolicious::Lite;

use FindBin;
use lib "$FindBin::Bin/lib";

use Ditaa;

get '/' => { 
    message => '',
    image_tag => '',
} => 'index';

post '/' => sub {
    my $self = shift;

    my $ditaa = Ditaa->new(
        bin => '/usr/bin/ditaa', java => '/usr/bin/java'
    );

    my $file = localtime();
    $ditaa->render_image(
        $self->param('content') || '', "./public/${file}.png"
    );

    $self->stash(
        image_tag => "<img src='/${file}.png' />",
        message => '',
    );
} => 'index';

app->start;
__DATA__

@@ index.html.ep
<!DOCTYPE html>
<html>
  <head><title>Ditaa Perl Web</title></head>
  <body>
    <h2>Ditaa Web Perl</h2>
    <p><%== $image_tag %></p>
    <form method="post">
        <p><strong>Enter with ditaa code here:</strong><br />
        <textarea name="content" rows="15" cols="80"></textarea></p>
        <input type="submit" value="Make Image" />
        <%= $message %>
    </form>
  </body>
</html>
