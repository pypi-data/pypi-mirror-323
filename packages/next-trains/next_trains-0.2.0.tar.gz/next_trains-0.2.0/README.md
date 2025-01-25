# Next Trains

An imagining of a combined Arrivals and Departure board.

![A screenshot of the next-trains app][screenshot]

My two-year-old loves trains - obviously - so any time we can swing past the station and see them is worth the detour.
This is a simple web app that calls a Rail Data Marketplace API getting the next few arrivals and departures to help us schedule a visit.
I then spruced it up a bit with a fun font to make it look a bit like a real Departures board.

## Installing

```sh
$ pip install next-trains

$ cat <<EOF >.env
RAIL_DATA_API_KEY={{ paste your API key here }}
DEFAULT_CRS={{ paste your home station's CRS here }}
EOF
```

## Running

```sh
$ trains
```

## Development

```sh
$ pip install -e .[dev]

$ ./lint-and-test
$ ./build-and-upload
```

## Credits

The data is from [Live Arrival and Departure Boards - Staff Version][api] by [Rail Delivery Group][rdg] under [an open licence][open-licence].

The fonts are [London TFL Dot Matrix Typeface][fonts] by [Sean Petykowski][petykowski] under [SIL Open Font License][fonts-license].

## License

Next Trains - An imagining of a combined Arrivals and Departure board.

Copyright (C) 2025 Mike Coats

This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License along with this program. If not, see [http://www.gnu.org/licenses/][agpl].

[screenshot]: ./example.png
[api]: https://raildata.org.uk/dashboard/dataProduct/P-8ce95b80-43ba-4ef7-b59a-6eb5d2bab061/overview
[rdg]: https://raildata.org.uk/dashboard/partnerDetails/1010/details
[open-licence]: ./vendor/api-licence.pdf
[fonts]: https://github.com/petykowski/London-Underground-Dot-Matrix-Typeface
[petykowski]: https://github.com/petykowski
[fonts-license]: https://github.com/petykowski/London-Underground-Dot-Matrix-Typeface/tree/master#license
[agpl]: http://www.gnu.org/licenses/